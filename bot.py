from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Configuration files
CONFIG_FILE = "satsuma_config.json"
MAIN_CONFIG_FILE = "config.json"

# Terminal Colors
class Colors:
    RESET = '\033[0m'
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    PURPLE = '\033[35m'

class Logger:
    @staticmethod
    def info(msg):
        print(f"{Colors.GREEN}[✓] {msg}{Colors.RESET}")

    @staticmethod
    def warn(msg):
        print(f"{Colors.YELLOW}[!] {msg}{Colors.RESET}")

    @staticmethod
    def error(msg):
        print(f"{Colors.RED}[✗] {msg}{Colors.RESET}")

    @staticmethod
    def success(msg):
        print(f"{Colors.GREEN}[+] {msg}{Colors.RESET}")

    @staticmethod
    def processing(msg):
        print(f"{Colors.CYAN}[⟳] {msg}{Colors.RESET}")

    @staticmethod
    def step(msg):
        print(f"{Colors.WHITE}[➤] {msg}{Colors.RESET}")

    @staticmethod
    def banner():
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("-" * 50)
        print(" Satsuma auto bot ")
        print(" powered by Zona Airdrop ")
        print(" Group @ZonaAirdr0p ")
        print("-" * 50)
        print(f"{Colors.RESET}\n")

log = Logger()

# Contract ABIs
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    }
]

SWAP_ROUTER_ABI = [
    {
        "name": "exactInputSingle",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {"name": "tokenIn", "type": "address"},
            {"name": "tokenOut", "type": "address"},
            {"name": "fee", "type": "uint24"},
            {"name": "recipient", "type": "address"},
            {"name": "deadline", "type": "uint256"},
            {"name": "amountIn", "type": "uint256"},
            {"name": "amountOutMinimum", "type": "uint256"},
            {"name": "sqrtPriceLimitX96", "type": "uint160"}
        ],
        "outputs": [{"name": "amountOut", "type": "uint256"}]
    },
    {
        "name": "multicall",
        "type": "function",
        "stateMutability": "payable",
        "inputs": [
            {
                "internalType": "bytes[]",
                "name": "data",
                "type": "bytes[]"
            }
        ],
        "outputs": [
            {
                "internalType": "bytes[]",
                "name": "results",
                "type": "bytes[]"
            }
        ]
    }
]

UNISWAP_V3_FACTORY_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "tokenA", "type": "address"},
            {"internalType": "address", "name": "tokenB", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"}
        ],
        "name": "getPool",
        "outputs": [
            {"internalType": "address", "name": "pool", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

LIQUIDITY_ROUTER_ABI = [
    {
        "inputs": [
            {"name": "tokenA", "type": "address"},
            {"name": "tokenB", "type": "address"},
            {"name": "deployer", "type": "address"},
            {"name": "recipient", "type": "address"},
            {"name": "amountADesired", "type": "uint256"},
            {"name": "amountBDesired", "type": "uint256"},
            {"name": "amountAMin", "type": "uint256"},
            {"name": "amountBMin", "type": "uint256"},
            {"name": "deadline", "type": "uint256"}
        ],
        "name": "addLiquidity",
        "outputs": [
            {"name": "amountA", "type": "uint256"},
            {"name": "amountB", "type": "uint256"},
            {"name": "liquidity", "type": "uint128"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes[]",
                "name": "data",
                "type": "bytes[]"
            }
        ],
        "name": "multicall",
        "outputs": [
            {
                "internalType": "bytes[]",
                "name": "results",
                "type": "bytes[]"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

VESUMA_ABI = [
    {
        "name": "create_lock",
        "inputs": [
            {"name": "_value", "type": "uint256"},
            {"name": "_unlock_time", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    },
    {
        "name": "increase_amount",
        "inputs": [{"name": "_value", "type": "uint256"}],
        "outputs": [],
        "type": "function"
    }
]

STAKING_ABI = [
    {
        "name": "stake",
        "inputs": [{"name": "_amount", "type": "uint256"}],
        "outputs": [],
        "type": "function"
    }
]

VOTING_ABI = [
    {
        "name": "vote",
        "inputs": [
            {"name": "gauge_addr", "type": "address"},
            {"name": "weight", "type": "uint256"}
        ],
        "outputs": [],
        "type": "function"
    }
]

class SatsumaBot:
    def __init__(self):
        self.config = self.load_config()
        self.w3 = self.initialize_provider()
        self.private_keys = self.get_private_keys()
        self.settings = self.load_user_settings()
        self.transaction_history = []

    def load_config(self):
        config = {
            "rpc": "https://rpc.testnet.citrea.xyz",
            "chain_id": 5115,
            "symbol": "cBTC",
            "explorer": "https://explorer.testnet.citrea.xyz",
            "swap_router": Web3.to_checksum_address("0x3012e9049d05b4b5369d690114d5a5861ebb85cb"),
            "uniswap_v3_factory": Web3.to_checksum_address("0x2668e310036E7E9110B9670d8a5E5A8f44d8525b"),
            "liquidity_router": Web3.to_checksum_address("0x55a4669cd6895EA25C174F13E1b49d69B4481704"),
            "pool_address": Web3.to_checksum_address("0x080c376e6aB309fF1a861e1c3F91F27b8D4f1443"),
            "usdc_address": Web3.to_checksum_address("0x2C8abD2A528D19AFc33d2eBA507c0F405c131335"),
            "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
            "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"),
            "vesuma_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567890"),
            "voting_contract": Web3.to_checksum_address("0x1234567890123456789012345678901234567891"),
            "staking_contract": Web3.to_checksum_address("0x1234567890123456789012345678901234567892"),
            "gauge_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567893")
        }
        
        try:
            with open(MAIN_CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            log.warn(f"Could not save config file: {str(e)}")
        
        return config

    def initialize_provider(self):
        try:
            w3 = Web3(Web3.HTTPProvider(self.config["rpc"]))
            if not w3.is_connected():
                raise Exception("Failed to connect to RPC")
            
            log.success(f"Connected to {self.config['rpc']}")
            log.info(f"Chain ID: {self.config['chain_id']}")
            return w3
        except Exception as e:
            log.error(f"Provider initialization failed: {str(e)}")
            sys.exit(1)

    def get_private_keys(self):
        private_keys = []
        key = os.getenv("PRIVATE_KEY_1")
        
        if not key or key == "your_private_key_here":
            log.error("No valid private key found in environment variables")
            log.info("Please set PRIVATE_KEY_1 in your .env file with your actual private key")
            
            # For demo purposes, ask for private key input
            key = input("Enter your private key (without 0x prefix): ")
            if not key:
                sys.exit(1)
        
        try:
            account = Web3().eth.account.from_key(key)
            log.success(f"Loaded private key for address: {account.address}")
            private_keys.append(key)
        except Exception as e:
            log.error(f"Invalid private key: {str(e)}")
            sys.exit(1)
        
        return private_keys

    def load_user_settings(self):
        user_settings = {
            "transaction_count": 0,
            "current_round": 0,
            "total_transactions": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "last_transaction_time": None
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    user_settings.update(data)
                    log.success(f"Loaded configuration: {user_settings['transaction_count']} transactions planned")
        except Exception as e:
            log.error(f"Failed to load settings: {str(e)}")
        
        return user_settings

    def save_user_settings(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
            log.success("Configuration saved successfully")
        except Exception as e:
            log.error(f"Failed to save settings: {str(e)}")

    def generate_random_amount(self):
        min_amount = 0.0001
        max_amount = 0.0002
        random_amount = random.uniform(min_amount, max_amount)
        return round(random_amount, 6)

    async def approve_token(self, account, token_address, spender_address, amount):
        try:
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            log.processing(f"Checking allowance for {token_address}")
            
            allowance = token_contract.functions.allowance(account.address, spender_address).call()
            if allowance >= amount:
                log.success("Sufficient allowance already exists")
                return {"success": True, "nonce": nonce}
            
            log.processing("Sending approval transaction...")
            
            approve_tx = token_contract.functions.approve(spender_address, amount).build_transaction({
                "from": account.address,
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing("Waiting for approval confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.success(f"Approval successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                return {"success": True, "nonce": nonce + 1}
            else:
                log.error("Approval transaction failed")
                return {"success": False, "nonce": nonce}
                
        except Exception as e:
            log.error(f"Approval error: {str(e)}")
            return {"success": False, "nonce": nonce if 'nonce' in locals() else 0}

    async def get_token_balance(self, token_address, account_address):
        try:
            token_contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
            balance = token_contract.functions.balanceOf(account_address).call()
            decimals = token_contract.functions.decimals().call()
            symbol = token_contract.functions.symbol().call()
            
            return {
                "balance": balance,
                "decimals": decimals,
                "symbol": symbol,
                "formatted": balance / (10 ** decimals)
            }
        except Exception as e:
            log.error(f"Error getting token balance: {str(e)}")
            return None
    
    async def perform_swap(self, private_key, token_in, token_out, amount_in):
        try:
            account = self.w3.eth.account.from_key(private_key)
            
            log.info(f"Performing swap for {account.address}")
            
            amount_in_wei = self.w3.to_wei(amount_in, 'ether')
            
            # Check token and cBTC balances first
            cbtc_balance = self.w3.eth.get_balance(account.address)
            if cbtc_balance < self.w3.to_wei(0.001, 'ether'): # Gas fee check
                log.error("Insufficient cBTC balance to pay for gas fees.")
                return {"success": False, "error": "Insufficient cBTC balance"}
            
            token_in_balance = await self.get_token_balance(token_in, account.address)
            if token_in_balance['balance'] < amount_in_wei:
                log.error(f"Insufficient {token_in_balance['symbol']} balance. Have {token_in_balance['formatted']:.6f}, need {amount_in:.6f}")
                return {"success": False, "error": f"Insufficient {token_in_balance['symbol']} balance"}
            
            # Approve token first
            approval_result = await self.approve_token(account, token_in, self.config["swap_router"], amount_in_wei)
            if not approval_result["success"]:
                return {"success": False, "error": "Approval failed"}
            
            # Prepare swap transaction
            swap_contract = self.w3.eth.contract(address=self.config["swap_router"], abi=SWAP_ROUTER_ABI)
            
            deadline = int(time.time()) + 300  # 5 minutes
            fee = 3000  # Standard 0.3% fee tier
            
            # Build the exactInputSingle parameters
            params = (
                token_in,
                token_out,
                fee,
                account.address,
                deadline,
                amount_in_wei,
                0,  # amountOutMinimum
                0   # sqrtPriceLimitX96
            )
            
            # Get the function object
            swap_func = swap_contract.functions.exactInputSingle(params)
            
            # Build the transaction
            nonce = self.w3.eth.get_transaction_count(account.address)
            swap_tx = swap_func.build_transaction({
                "from": account.address,
                "gas": 300000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce,
                "value": 0  # Ensure no ETH/cBTC is sent
            })

            # Simulate transaction before sending
            try:
                log.processing("Simulating transaction...")
                self.w3.eth.call(swap_tx, block_identifier='latest')
                log.success("Simulation successful. Transaction is likely to pass.")
            except Exception as e:
                log.error(f"Transaction simulation failed. Reason: {str(e)}")
                return {"success": False, "error": str(e)}

            # Send the transaction
            signed_tx = self.w3.eth.account.sign_transaction(swap_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.processing("Waiting for swap confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.success(f"Swap successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "swap",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error("Swap transaction failed")
                return {"success": False, "error": "Transaction failed"}
                
        except Exception as e:
            log.error(f"Swap error: {str(e)}")
            return {"success": False, "error": str(e)}

    # ... [rest of the code remains exactly the same] ...

async def run():
    bot = SatsumaBot()
    await bot.run()

if __name__ == "__run__":
    asyncio.run(run())
