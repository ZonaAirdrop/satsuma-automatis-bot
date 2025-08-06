from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)
load_dotenv()

# Configuration files
CONFIG_FILE = "satsuma_config.json"
MAIN_CONFIG_FILE = "config.json"

# Terminal Colors
class Colors:
    RESET = Style.RESET_ALL
    BOLD = Style.BRIGHT
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    RED = Fore.RED
    CYAN = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE = Fore.WHITE
    BRIGHT_GREEN = Fore.LIGHTGREEN_EX
    BRIGHT_MAGENTA = Fore.LIGHTMAGENTA_EX
    BRIGHT_WHITE = Fore.LIGHTWHITE_EX
    BRIGHT_BLACK = Fore.LIGHTBLACK_EX

class Logger:
    @staticmethod
    def log(label, symbol, msg, color):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.BRIGHT_BLACK}[{timestamp}]{Colors.RESET} {color}[{symbol}] {msg}{Colors.RESET}")

    @staticmethod
    def info(msg): Logger.log("INFO", "✓", msg, Colors.GREEN)
    @staticmethod
    def warn(msg): Logger.log("WARN", "!", msg, Colors.YELLOW)
    @staticmethod
    def error(msg): Logger.log("ERR", "✗", msg, Colors.RED)
    @staticmethod
    def success(msg): Logger.log("OK", "+", msg, Colors.GREEN)
    @staticmethod
    def loading(msg): Logger.log("LOAD", "⟳", msg, Colors.CYAN)
    @staticmethod
    def step(msg): Logger.log("STEP", "➤", msg, Colors.WHITE)
    @staticmethod
    def action(msg): Logger.log("ACTION", "↪️", msg, Colors.CYAN)
    @staticmethod
    def actionSuccess(msg): Logger.log("ACTION", "✅", msg, Colors.GREEN)

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
    # ExactInputSingle for WBTC->USDC
    {
        "inputs": [
            {
                "components": [
                    {"name": "tokenIn", "type": "address"},
                    {"name": "tokenOut", "type": "address"},
                    {"name": "deployer", "type": "address"},
                    {"name": "recipient", "type": "address"},
                    {"name": "deadline", "type": "uint256"},
                    {"name": "amountIn", "type": "uint256"},
                    {"name": "amountOutMinimum", "type": "uint256"},
                    {"name": "limitSqrtPrice", "type": "uint160"}
                ],
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInputSingle",
        "outputs": [{"name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    },
    # Multicall for complex swaps
    {
        "inputs": [{"name": "data", "type": "bytes[]"}],
        "name": "multicall",
        "outputs": [{"name": "results", "type": "bytes[]"}],
        "stateMutability": "payable",
        "type": "function"
    },
    # Callback
    {
        "inputs": [
            {"name": "amount0Delta", "type": "int256"},
            {"name": "amount1Delta", "type": "int256"},
            {"name": "_data", "type": "bytes"}
        ],
        "name": "algebraSwapCallback",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

WRAPPER_ABI = [
    {
        "inputs": [],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "amount", "type": "uint256"}
        ],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
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
            "liquidity_router": Web3.to_checksum_address("0x55a4669cd6895EA25C174F13E1b49d69B4481704"),
            "pool_address": Web3.to_checksum_address("0x080c376e6aB309fF1a861e1c3F91F27b8D4f1443"),
            "usdc_address": Web3.to_checksum_address("0x2C8abD2A528D19AFc33d2eBA507c0F405c131335"),
            "wcbtc_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),
            "suma_address": Web3.to_checksum_address("0xdE4251dd68e1aD5865b14Dd527E54018767Af58a"),
            "s33_address": Web3.to_checksum_address("0xb93B80d59c2FB3eb23817d4A27841eF8788826f0"),
            "wrapper_address": Web3.to_checksum_address("0x8d0c9d1c17ae5e40fff9be350f57840e9e66cd93"),  # WCBTC is wrapper for CBTC
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
            
            log.loading(f"Checking allowance for {token_address}")
            
            allowance = token_contract.functions.allowance(account.address, spender_address).call()
            if allowance >= amount:
                log.success("Sufficient allowance already exists")
                return {"success": True, "nonce": nonce}
            
            log.loading("Sending approval transaction...")
            
            approve_tx = token_contract.functions.approve(spender_address, amount).build_transaction({
                "from": account.address,
                "gas": 100000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.loading("Waiting for approval confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.actionSuccess(f"Approval successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
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
            
            amount_in_wei = int(amount_in * 10**18)
            
            # Approve token first
            approval_result = await self.approve_token(account, token_in, self.config["swap_router"], amount_in_wei)
            if not approval_result["success"]:
                return {"success": False, "error": "Approval failed"}
            
            swap_contract = self.w3.eth.contract(address=self.config["swap_router"], abi=SWAP_ROUTER_ABI)
            deadline = int(time.time()) + 300  # 5 minutes
            
            # Determine which swap method to use based on token pair
            if (token_in.lower() == self.config["wcbtc_address"].lower() and 
                token_out.lower() == self.config["usdc_address"].lower()):
                # WBTC -> USDC uses exactInputSingle
                swap_params = {
                    "tokenIn": token_in,
                    "tokenOut": token_out,
                    "deployer": account.address,
                    "recipient": account.address,
                    "deadline": deadline,
                    "amountIn": amount_in_wei,
                    "amountOutMinimum": 0,
                    "limitSqrtPrice": 0
                }
                
                nonce = approval_result["nonce"]
                
                swap_tx = swap_contract.functions.exactInputSingle(swap_params).build_transaction({
                    "from": account.address,
                    "gas": 300000,
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": nonce
                })
            else:
                # All other swaps use multicall
                # For simplicity, we'll just encode a single swap in the multicall
                # In a real implementation, you might have more complex routing
                swap_params = {
                    "tokenIn": token_in,
                    "tokenOut": token_out,
                    "deployer": account.address,
                    "recipient": account.address,
                    "deadline": deadline,
                    "amountIn": amount_in_wei,
                    "amountOutMinimum": 0,
                    "limitSqrtPrice": 0
                }
                
                nonce = approval_result["nonce"]
                
                # Encode the swap as a multicall
                swap_data = swap_contract.encodeABI(
                    fn_name="exactInputSingle",
                    args=[swap_params]
                )
                
                swap_tx = swap_contract.functions.multicall([swap_data]).build_transaction({
                    "from": account.address,
                    "gas": 400000,  # Higher gas for multicall
                    "gasPrice": self.w3.eth.gas_price,
                    "nonce": nonce
                })
            
            signed_tx = self.w3.eth.account.sign_transaction(swap_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.loading("Waiting for swap confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.actionSuccess(f"Swap successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
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

    async def wrap_cbtc(self, private_key, amount):
        try:
            account = self.w3.eth.account.from_key(private_key)
            amount_wei = self.w3.to_wei(amount, 'ether')
            
            wrapper_contract = self.w3.eth.contract(
                address=self.config["wrapper_address"],
                abi=WRAPPER_ABI
            )
            
            nonce = self.w3.eth.get_transaction_count(account.address)
            
            wrap_tx = wrapper_contract.functions.deposit().build_transaction({
                "from": account.address,
                "value": amount_wei,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(wrap_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.loading("Waiting for wrap confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.actionSuccess(f"Wrap successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "wrap",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error("Wrap transaction failed")
                return {"success": False, "error": "Transaction failed"}
                
        except Exception as e:
            log.error(f"Wrap error: {str(e)}")
            return {"success": False, "error": str(e)}

    async def unwrap_wcbtc(self, private_key, amount):
        try:
            account = self.w3.eth.account.from_key(private_key)
            amount_wei = int(amount * 10**18)  # Assuming WBTC has 18 decimals
            
            # First approve the wrapper to spend WBTC
            approval_result = await self.approve_token(
                account,
                self.config["wcbtc_address"],
                self.config["wrapper_address"],
                amount_wei
            )
            
            if not approval_result["success"]:
                return {"success": False, "error": "Approval failed"}
            
            wrapper_contract = self.w3.eth.contract(
                address=self.config["wrapper_address"],
                abi=WRAPPER_ABI
            )
            
            nonce = approval_result["nonce"]
            
            unwrap_tx = wrapper_contract.functions.withdraw(amount_wei).build_transaction({
                "from": account.address,
                "gas": 200000,
                "gasPrice": self.w3.eth.gas_price,
                "nonce": nonce
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(unwrap_tx, private_key=private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            log.loading("Waiting for unwrap confirmation...")
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt["status"] == 1:
                log.actionSuccess(f"Unwrap successful! Tx: {self.config['explorer']}/tx/{tx_hash.hex()}")
                self.transaction_history.append({
                    "type": "unwrap",
                    "tx_hash": tx_hash.hex(),
                    "timestamp": datetime.now().isoformat(),
                    "status": "success"
                })
                return {"success": True, "tx_hash": tx_hash.hex()}
            else:
                log.error("Unwrap transaction failed")
                return {"success": False, "error": "Transaction failed"}
                
        except Exception as e:
            log.error(f"Unwrap error: {str(e)}")
            return {"success": False, "error": str(e)}

    def display_menu(self):
        print(f"\n{Colors.YELLOW}=== Satsuma DeFi Bot Menu ==={Colors.RESET}")
        print(f"{Colors.YELLOW}1. Start Automated Swaps{Colors.RESET}")
        print(f"{Colors.YELLOW}2. Set Transaction Count{Colors.RESET}")
        print(f"{Colors.YELLOW}3. Manual Swap{Colors.RESET}")
        print(f"{Colors.YELLOW}4. Add Liquidity{Colors.RESET}")
        print(f"{Colors.YELLOW}5. Convert SUMA to veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}6. Stake veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}7. Vote with veSUMA{Colors.RESET}")
        print(f"{Colors.YELLOW}8. Wrap CBTC to WCBTC{Colors.RESET}")
        print(f"{Colors.YELLOW}9. Unwrap WCBTC to CBTC{Colors.RESET}")
        print(f"{Colors.YELLOW}10. Show Balances{Colors.RESET}")
        print(f"{Colors.YELLOW}11. Transaction History{Colors.RESET}")
        print(f"{Colors.YELLOW}12. Exit{Colors.RESET}")
        print(f"{Colors.YELLOW}{'='*35}{Colors.RESET}")

    async def handle_menu_option(self, option):
        try:
            if option == "1":
                await self.start_automated_swaps()
            
            elif option == "2":
                try:
                    count = int(input("Enter transaction count: "))
                    if count > 0:
                        self.settings["transaction_count"] = count
                        self.save_user_settings()
                        log.success(f"Transaction count set to {count}")
                    else:
                        log.error("Transaction count must be positive")
                except ValueError:
                    log.error("Invalid transaction count")
            
            elif option == "3":
                print(f"\n{Colors.CYAN}=== Manual Swap ==={Colors.RESET}")
                print("Token addresses:")
                print(f"USDC: {self.config['usdc_address']}")
                print(f"WCBTC: {self.config['wcbtc_address']}")
                print(f"SUMA: {self.config['suma_address']}")
                print(f"S33: {self.config['s33_address']}")
                
                token_in = input("Enter token in address: ").strip()
                token_out = input("Enter token out address: ").strip()
                
                try:
                    amount = float(input("Enter amount: "))
                    if amount > 0:
                        result = await self.perform_swap(self.private_keys[0], token_in, token_out, amount)
                        if result["success"]:
                            log.actionSuccess("Manual swap completed successfully")
                        else:
                            log.error(f"Manual swap failed: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Amount must be positive")
                except ValueError:
                    log.error("Invalid amount")
            
            elif option == "8":
                print(f"\n{Colors.CYAN}=== Wrap CBTC to WCBTC ==={Colors.RESET}")
                try:
                    amount = float(input("Enter CBTC amount to wrap: "))
                    if amount > 0:
                        result = await self.wrap_cbtc(self.private_keys[0], amount)
                        if result["success"]:
                            log.actionSuccess("Wrap completed successfully")
                        else:
                            log.error(f"Wrap failed: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Amount must be positive")
                except ValueError:
                    log.error("Invalid amount")
            
            elif option == "9":
                print(f"\n{Colors.CYAN}=== Unwrap WCBTC to CBTC ==={Colors.RESET}")
                try:
                    amount = float(input("Enter WCBTC amount to unwrap: "))
                    if amount > 0:
                        result = await self.unwrap_wcbtc(self.private_keys[0], amount)
                        if result["success"]:
                            log.actionSuccess("Unwrap completed successfully")
                        else:
                            log.error(f"Unwrap failed: {result.get('error', 'Unknown error')}")
                    else:
                        log.error("Amount must be positive")
                except ValueError:
                    log.error("Invalid amount")
            
            # ... (rest of the menu options remain similar)

            elif option == "12":
                log.info("Exiting Satsuma Bot...")
                return False
            
            else:
                log.error("Invalid option. Please choose 1-12.")
        
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
        
        return True

    async def run(self):
        self.display_welcome_screen()
        log.success("Satsuma DeFi Bot initialized successfully!")
        
        while True:
            try:
                self.display_menu()
                choice = input(f"{Colors.WHITE}[➤] Select option (1-12): {Colors.RESET}").strip()
                
                if not choice:
                    continue
                
                should_continue = await self.handle_menu_option(choice)
                if not should_continue:
                    break
                
            except KeyboardInterrupt:
                log.info("\nBot stopped by user")
                break
            except Exception as e:
                log.error(f"Unexpected error: {str(e)}")
                continue

    def display_welcome_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        now = datetime.now()
        print(f"{Colors.BRIGHT_GREEN}{Colors.BOLD}")
        print("  ╔══════════════════════════════════════╗")
        print("  ║           S A T S U M A              ║")
        print("  ║                                      ║")
        print(f"  ║     {Colors.YELLOW}{now.strftime('%H:%M:%S %d.%m.%Y')}{Colors.BRIGHT_GREEN}           ║")
        print("  ║                                      ║")
        print("  ║     CITREA TESTNET AUTOMATION        ║")
        print(f"  ║   {Colors.BRIGHT_WHITE}ZonaAirdrop{Colors.BRIGHT_GREEN}  |  t.me/ZonaAirdr0p   ║")
        print("  ╚══════════════════════════════════════╝")
        print(f"{Colors.RESET}")

async def main():
    bot = SatsumaBot()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())