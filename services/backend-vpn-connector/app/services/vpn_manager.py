import subprocess
import os
import logging
import asyncio
from typing import Optional, Dict
from ..models.vpn import VPNConfig
from sqlalchemy.orm import Session
import re
import time

logger = logging.getLogger(__name__)

class VPNManager:
    def __init__(self):
        self.vpn_config_dir = "/etc/openvpn/configs"
        self.active_connections: Dict[str, Dict] = {}
        self.monitor_tasks: Dict[str, asyncio.Task] = {}
        
        # Create config directory if it doesn't exist
        os.makedirs(self.vpn_config_dir, exist_ok=True)
        os.makedirs("/var/log/openvpn", exist_ok=True)

    async def _setup_routing(self, interface: str, target_network: str) -> None:
        """Set up routing rules for the VPN interface."""
        try:
            cmds = [
                f"ip route add {target_network} dev {interface}",
                f"iptables -A FORWARD -i {interface} -j ACCEPT",
                f"iptables -A FORWARD -o {interface} -j ACCEPT",
                f"iptables -t nat -A POSTROUTING -o {interface} -j MASQUERADE"
            ]
            
            for cmd in cmds:
                process = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise RuntimeError(f"Failed to execute {cmd}: {stderr.decode()}")
                    
            logger.info(f"Successfully set up routing for {interface}")
            
        except Exception as e:
            logger.error(f"Failed to set up routing: {str(e)}")
            raise

    async def monitor_connection(self, config_id: str, db: Session):
        """Monitor VPN connection and update status."""
        while config_id in self.active_connections:
            try:
                conn_info = self.active_connections[config_id]
                process = conn_info['process']
                log_file = f"/var/log/openvpn/{config_id}.log"

                # Check if process is still running
                if process.poll() is not None:
                    logger.error(f"VPN process terminated unexpectedly for config {config_id}")
                    await self._handle_connection_failure(config_id, db)
                    break

                # Check OpenVPN logs for connection status
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        logs = f.read()
                        if "Initialization Sequence Completed" in logs:
                            conn_info['status'] = 'connected'
                        elif "Connection reset" in logs or "AUTH_FAILED" in logs:
                            await self._handle_connection_failure(config_id, db)
                            break

            except Exception as e:
                logger.error(f"Error monitoring VPN connection {config_id}: {str(e)}")
                await self._handle_connection_failure(config_id, db)
                break

            await asyncio.sleep(5)  # Check every 5 seconds

    async def _handle_connection_failure(self, config_id: str, db: Session):
        """Handle VPN connection failure."""
        try:
            # Update database status
            config = db.query(VPNConfig).filter(VPNConfig.config_id == config_id).first()
            if config:
                config.status = 'error'
                db.commit()

            # Clean up connection
            if config_id in self.active_connections:
                conn_info = self.active_connections[config_id]
                process = conn_info['process']
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                del self.active_connections[config_id]

            # Stop monitoring
            if config_id in self.monitor_tasks:
                self.monitor_tasks[config_id].cancel()
                del self.monitor_tasks[config_id]

        except Exception as e:
            logger.error(f"Error handling connection failure for {config_id}: {str(e)}")

    async def connect(self, config: VPNConfig, db: Session) -> Dict:
        """Connect to VPN using the provided configuration."""
        try:
            config_path = os.path.join(self.vpn_config_dir, f"{config.config_id}.ovpn")
            log_file = f"/var/log/openvpn/{config.config_id}.log"
            
            # Check if config file exists
            if not os.path.exists(config_path):
                raise Exception("VPN configuration file not found")
            
            # Check if already connected
            if str(config.config_id) in self.active_connections:
                return {
                    "status": "connected",
                    "message": "VPN already connected"
                }
            
            # Update status to connecting
            config.status = 'connecting'
            db.commit()
            
            # Start OpenVPN process
            process = subprocess.Popen(
                [
                    'openvpn',
                    '--config', config_path,
                    '--log', log_file
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Store connection info
            self.active_connections[str(config.config_id)] = {
                'process': process,
                'started_at': time.time(),
                'status': 'connecting'
            }
            
            # Start monitoring
            monitor_task = asyncio.create_task(
                self.monitor_connection(str(config.config_id), db)
            )
            self.monitor_tasks[str(config.config_id)] = monitor_task
            
            # Update status to connected
            config.status = 'connected'
            db.commit()
            
            return {
                "status": "connected",
                "message": "VPN connection established",
                "config_id": str(config.config_id)
            }
            
        except Exception as e:
            logger.error(f"Error connecting to VPN: {str(e)}")
            config.status = 'error'
            db.commit()
            raise

    async def get_status(self, config: VPNConfig) -> Dict:
        """Get current VPN connection status."""
        try:
            conn_info = self.active_connections.get(str(config.config_id))
            is_connected = conn_info is not None
            
            status_info = {
                "config_id": str(config.config_id),
                "status": config.status,
                "is_active": is_connected,
                "name": config.name
            }
            
            if is_connected:
                status_info.update({
                    "connected_since": conn_info['started_at'],
                    "current_status": conn_info['status']
                })
                
                # Add connection statistics if available
                log_file = f"/var/log/openvpn/{config.config_id}.log"
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        logs = f.read()
                        # Extract bytes sent/received if available
                        bytes_stats = re.findall(r"(\d+) bytes received, (\d+) bytes sent", logs)
                        if bytes_stats:
                            status_info["bytes_received"] = bytes_stats[-1][0]
                            status_info["bytes_sent"] = bytes_stats[-1][1]
            
            return status_info
            
        except Exception as e:
            logger.error(f"Error getting VPN status: {str(e)}")
            raise

    async def get_interface_info(self, config: VPNConfig) -> Dict:
        """Get VPN interface information."""
        try:
            conn_info = self.active_connections.get(str(config.config_id))
            if not conn_info:
                raise Exception("VPN connection not active")
            
            # Get interface name from OpenVPN log
            log_file = f"/var/log/openvpn/{config.config_id}.log"
            if not os.path.exists(log_file):
                raise Exception("VPN log file not found")
            
            with open(log_file, 'r') as f:
                logs = f.read()
                # Extract interface name
                interface_match = re.search(r"TUN/TAP device (tun\d+) opened", logs)
                if not interface_match:
                    raise Exception("Could not determine VPN interface")
                
                interface = interface_match.group(1)
            
            # Get interface details
            try:
                import netifaces
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET not in addrs:
                    raise Exception(f"No IPv4 address assigned to {interface}")
                
                ip_info = addrs[netifaces.AF_INET][0]
                
                # Get routes
                import subprocess
                route_output = subprocess.check_output(['ip', 'route', 'show', 'dev', interface])
                routes = route_output.decode().splitlines()
                
                return {
                    "interface": interface,
                    "local_ip": ip_info['addr'],
                    "netmask": ip_info['netmask'],
                    "routes": routes
                }
                
            except Exception as e:
                logger.error(f"Error getting interface details: {str(e)}")
                return {
                    "interface": interface,
                    "local_ip": None,
                    "netmask": None,
                    "routes": []
                }
            
        except Exception as e:
            logger.error(f"Error getting interface info: {str(e)}")
            raise 

vpn_manager = VPNManager()