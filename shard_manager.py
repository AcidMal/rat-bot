#!/usr/bin/env python3
"""
Shard Manager for Rat Bot
This script helps manage multiple bot instances across different shards.
Useful for large bots with 2500+ servers.
"""

import asyncio
import logging
import os
import sys
import subprocess
import time
import signal
from typing import List, Dict
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler('logs/shard_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('shard_manager')

class ShardManager:
    def __init__(self, total_shards: int = None):
        self.total_shards = total_shards
        self.processes: Dict[int, subprocess.Popen] = {}
        self.running = True
        
        # Handle shutdown signals
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.stop_all_shards()
        sys.exit(0)
    
    def calculate_shard_count(self) -> int:
        """Calculate the optimal number of shards based on guild count."""
        # This is a simplified calculation
        # In practice, you might want to use Discord's recommended shard count
        # or calculate based on your bot's actual guild count
        
        if self.total_shards:
            return self.total_shards
        
        # Default to 1 shard for small bots
        # For large bots, Discord recommends (guild_count + 9999) // 2500
        return 1
    
    def start_shard(self, shard_id: int) -> subprocess.Popen:
        """Start a single shard process."""
        env = os.environ.copy()
        env['SHARD_ID'] = str(shard_id)
        env['SHARD_COUNT'] = str(self.calculate_shard_count())
        
        logger.info(f"Starting shard {shard_id}")
        
        process = subprocess.Popen(
            [sys.executable, 'bot.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def start_all_shards(self):
        """Start all shard processes."""
        shard_count = self.calculate_shard_count()
        logger.info(f"Starting {shard_count} shard(s)")
        
        for shard_id in range(shard_count):
            try:
                process = self.start_shard(shard_id)
                self.processes[shard_id] = process
                logger.info(f"Started shard {shard_id} (PID: {process.pid})")
                
                # Small delay between starting shards to avoid rate limits
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to start shard {shard_id}: {e}")
    
    def stop_shard(self, shard_id: int):
        """Stop a single shard process."""
        if shard_id in self.processes:
            process = self.processes[shard_id]
            logger.info(f"Stopping shard {shard_id} (PID: {process.pid})")
            
            try:
                process.terminate()
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Shard {shard_id} didn't terminate gracefully, forcing...")
                process.kill()
            except Exception as e:
                logger.error(f"Error stopping shard {shard_id}: {e}")
            
            del self.processes[shard_id]
    
    def stop_all_shards(self):
        """Stop all shard processes."""
        logger.info("Stopping all shards...")
        
        for shard_id in list(self.processes.keys()):
            self.stop_shard(shard_id)
        
        logger.info("All shards stopped")
    
    def restart_shard(self, shard_id: int):
        """Restart a single shard."""
        logger.info(f"Restarting shard {shard_id}")
        self.stop_shard(shard_id)
        time.sleep(2)
        
        try:
            process = self.start_shard(shard_id)
            self.processes[shard_id] = process
            logger.info(f"Restarted shard {shard_id} (PID: {process.pid})")
        except Exception as e:
            logger.error(f"Failed to restart shard {shard_id}: {e}")
    
    def monitor_shards(self):
        """Monitor shard processes and restart if needed."""
        while self.running:
            for shard_id, process in list(self.processes.items()):
                if process.poll() is not None:
                    logger.warning(f"Shard {shard_id} crashed (exit code: {process.returncode})")
                    logger.info(f"Restarting shard {shard_id}...")
                    self.restart_shard(shard_id)
            
            time.sleep(10)  # Check every 10 seconds
    
    def get_shard_status(self) -> Dict[str, any]:
        """Get status of all shards."""
        status = {}
        
        for shard_id, process in self.processes.items():
            if process.poll() is None:
                status[f"shard_{shard_id}"] = {
                    "status": "running",
                    "pid": process.pid
                }
            else:
                status[f"shard_{shard_id}"] = {
                    "status": "crashed",
                    "exit_code": process.returncode
                }
        
        return status
    
    def print_status(self):
        """Print current shard status."""
        status = self.get_shard_status()
        logger.info("=== Shard Status ===")
        
        for shard_name, shard_info in status.items():
            if shard_info["status"] == "running":
                logger.info(f"{shard_name}: Running (PID: {shard_info['pid']})")
            else:
                logger.error(f"{shard_name}: Crashed (Exit Code: {shard_info['exit_code']})")
        
        logger.info("===================")

def main():
    """Main function for the shard manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rat Bot Shard Manager')
    parser.add_argument('--shards', type=int, help='Number of shards to run')
    parser.add_argument('--status', action='store_true', help='Show shard status and exit')
    parser.add_argument('--restart', type=int, help='Restart a specific shard')
    
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    manager = ShardManager(total_shards=args.shards)
    
    if args.status:
        # This would need to be implemented to read from a status file
        # since the manager process would need to be running
        logger.info("Status checking not implemented in this version")
        return
    
    if args.restart is not None:
        # This would need the manager to be running
        logger.info("Restart functionality requires the manager to be running")
        return
    
    try:
        logger.info("Starting Rat Bot Shard Manager...")
        manager.start_all_shards()
        
        # Start monitoring in a separate thread
        import threading
        monitor_thread = threading.Thread(target=manager.monitor_shards, daemon=True)
        monitor_thread.start()
        
        # Main loop
        while manager.running:
            time.sleep(30)  # Print status every 30 seconds
            manager.print_status()
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Shard manager error: {e}")
    finally:
        manager.stop_all_shards()
        logger.info("Shard manager stopped")

if __name__ == "__main__":
    main() 