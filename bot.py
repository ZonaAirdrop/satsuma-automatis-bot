from web3 import Web3
from dotenv import load_dotenv
import asyncio
import random
import time
import sys
import os
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from datetime import datetime, timedelta

# Initialize rich console
console = Console()

# Load environment variables
load_dotenv()

# Configuration files
CONFIG_FILE = "satsuma_config.json"
MAIN_CONFIG_FILE = "config.json"

# Color scheme with icons
class Logger:
    @staticmethod
    def success(message):
        console.print(f"[green]✓[/green] [white]{message}[/white]")
    
    @staticmethod
    def info(message):
        console.print(f"[cyan]ℹ[/cyan] [white]{message}[/white]")
    
    @staticmethod
    def warning(message):
        console.print(f"[yellow]![/yellow] [white]{message}[/white]")
    
    @staticmethod
    def error(message):
        console.print(f"[red]✗[/red] [white]{message}[/white]")
    
    @staticmethod
    def processing(message):
        console.print(f"[blue]⟳[/blue] [white]{message}[/white]")
    
    @staticmethod
    def arrow(message):
        console.print(f"[magenta]➤[/magenta] [white]{message}[/white]")
    
    @staticmethod
    def return_arrow(message):
        console.print(f"[cyan]↪️[/cyan] [white]{message}[/white]")
    
    @staticmethod
    def check(message):
        console.print(f"[green]✅[/green] [white]{message}[/white]")

# Initialize logger
log = Logger()

# === Animated Banner ===
def display_banner():
    banner_text = """
███████╗ █████╗ ████████╗███████╗██╗   ██╗███╗   ███╗ █████╗ 
██╔════╝██╔══██╗╚══██╔══╝██╔════╝██║   ██║████╗ ████║██╔══██╗
███████╗███████║   ██║   ███████╗██║   ██║██╔████╔██║███████║
╚════██║██╔══██║   ██║   ╚════██║██║   ██║██║╚██╔╝██║██╔══██║
███████║██║  ██║   ██║   ███████║╚██████╔╝██║ ╚═╝ ██║██║  ██║
╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
    """
    
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Display banner with animation
    banner_panel = Panel(
        Align.center(f"[bold cyan]{banner_text}[/bold cyan]\n[bold green]COMPREHENSIVE DEFI BOT[/bold green]\n[dim]Swap • Liquidity • Staking • Voting[/dim]"),
        border_style="bright_cyan"
    )
    console.print(banner_panel)
    
    # Loading animation
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Initializing bot...", total=None)
        time.sleep(2)
        progress.update(task, description="Loading configuration...")
        time.sleep(1)
        progress.update(task, description="Connecting to blockchain...")
        time.sleep(1)
    
    log.success("Satsuma DeFi Bot initialized successfully!")
    console.print()

# === Main Menu ===
def display_menu():
    table = Table(
        title="[bold blue]🚀 Satsuma DeFi Bot Menu[/bold blue]",
        style="cyan",
        title_justify="center",
        show_header=False,
        expand=True,
        border_style="bright_cyan"
    )
    table.add_column(justify="center", style="white")
    
    options = [
        "1. 🔄 Start Automated Swaps",
        "2. ⚙️  Set Transaction Count",
        "3. 💱 Manual Swap",
        "4. 💧 Add Liquidity",
        "5. 🔒 Convert SUMA to veSUMA",
        "6. 🥩 Stake veSUMA",
        "7. 🗳️  Vote with veSUMA",
        "8. 📊 View Balances",
        "9. 📈 Transaction History",
        "10. ❌ Exit"
    ]
    
    for opt in options:
        table.add_row(opt)
    
    console.print(table)
    console.print()
    choice = console.input("[bold magenta]➤ Select option (1-10): [/bold magenta]")
    return choice

# Load or initialize user settings
def load_user_settings():
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

# Save user settings
def save_user_settings(settings):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        log.success("Configuration saved successfully")
    except Exception as e:
        log.error(f"Failed to save settings: {str(e)}")

# Generate random amount for swaps
def generate_random_amount():
    min_amount = 0.0001
    max_amount = 0.0002
    random_amount = random.uniform(min_amount, max_amount)
    return round(random_amount, 6)

# Load blockchain configuration
def load_config():
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
        "vesuma_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567890"),
        "voting_contract": Web3.to_checksum_address("0x1234567890123456789012345678901234567891"),
        "staking_contract": Web3.to_checksum_address("0x1234567890123456789012345678901234567892"),
        "gauge_address": Web3.to_checksum_address("0x1234567890123456789012345678901234567893")
    }
    
    # Save config for reference
    try:
        with open(MAIN_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        log.warning(f"Could not save config file: {str(e)}")
    
    return config

# Initialize Web3 provider
def initialize_provider(config):
    try:
        w3 = Web3(Web3.HTTPProvider(config["rpc"]))
        if not w3.is_connected():
            raise Exception("Failed to connect to RPC")
        
        log.success(f"Connected to {config['rpc']}")
        log.info(f"Chain ID: {config['chain_id']}")
        return w3
    except Exception as e:
        log.error(f"Provider initialization failed: {str(e)}")
        sys.exit(1)

# Load private keys from environment
def get_private_keys():
    private_keys = []
    key = os.getenv("PRIVATE_KEY_1")
    
    if not key:
        log.error("No private key found in environment variables")
        log.info("Please set PRIVATE_KEY_1 in your .env file")
        sys.exit(1)
    
    try:
        account = Web3().eth.account.from_key(key)
        log.success(f"Loaded private key for address: {account.address}")
        private_keys.append(key)
    except Exception as e:
        log.error(f"Invalid private key: {str(e)}")
        sys.exit(1)
    
    return private_keys

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
    },
    {
        "name": "withdraw",
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

# Token approval function
async def approve_token(w3, config, account, token_address, spender_address, amount):
    try:
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
        nonce = w3.eth.get_transaction_count(account.address)
        
        log.processing(f"Checking allowance for {token_address}")
        
        allowance = token_contract.functions.allowance(account.address, spender_address).call()
        if allowance >= amount:
            log.success("Sufficient allowance already exists")
            return {"success": True, "nonce": nonce}
        
        log.processing("Sending approval transaction...")
        
        approve_tx = token_contract.functions.approve(spender_address, amount).build_transaction({
            "from": account.address,
            "gas": 100000,
            "gasPrice": w3.eth.gas_price,
            "nonce": nonce
        })
        
        signed_tx = w3.eth.account.sign_transaction(approve_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for approval confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.success(f"Approval successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return {"success": True, "nonce": nonce + 1}
        else:
            log.error("Approval transaction failed")
            return {"success": False, "nonce": nonce}
            
    except Exception as e:
        log.error(f"Approval error: {str(e)}")
        return {"success": False, "nonce": nonce if 'nonce' in locals() else 0}

# Get token balance
async def get_token_balance(w3, token_address, account_address):
    try:
        token_contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
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

# Swap function
async def perform_swap(w3, config, private_key, token_in, token_out, amount_in):
    try:
        account = w3.eth.account.from_key(private_key)
        
        log.info(f"Performing swap for {account.address}")
        log.arrow(f"Swapping {amount_in} {token_in} -> {token_out}")
        
        # Get token contracts
        token_in_contract = w3.eth.contract(address=config[f"{token_in.lower()}_address"], abi=ERC20_ABI)
        token_in_decimals = token_in_contract.functions.decimals().call()
        
        # Convert amount to wei
        amount_in_wei = int(amount_in * (10 ** token_in_decimals))
        
        # Check balance
        balance_info = await get_token_balance(w3, config[f"{token_in.lower()}_address"], account.address)
        if balance_info["balance"] < amount_in_wei:
            log.error(f"Insufficient {token_in} balance")
            return False
        
        # Approve token
        approval = await approve_token(
            w3, config, account, 
            config[f"{token_in.lower()}_address"], 
            config["swap_router"],
            amount_in_wei * 2
        )
        
        if not approval["success"]:
            log.error("Token approval failed")
            return False
        
        # Prepare swap parameters
        swap_router = w3.eth.contract(address=config["swap_router"], abi=SWAP_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60  # 20 minutes
        
        params = (
            config[f"{token_in.lower()}_address"],
            config[f"{token_out.lower()}_address"],
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            account.address,
            deadline,
            amount_in_wei,
            0,  # amountOutMinimum
            0   # limitSqrtPrice
        )
        
        # Execute swap
        log.processing("Executing swap transaction...")
        
        swap_tx = swap_router.functions.exactInputSingle(params).build_transaction({
            "from": account.address,
            "value": 0,
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "nonce": approval["nonce"]
        })
        
        signed_tx = w3.eth.account.sign_transaction(swap_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for swap confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.check(f"Swap successful! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return True
        else:
            log.error("Swap transaction failed")
            return False
            
    except Exception as e:
        log.error(f"Swap error: {str(e)}")
        return False

# Add liquidity function
async def add_liquidity(w3, config, private_key, token_a, token_b, amount_a, amount_b):
    try:
        account = w3.eth.account.from_key(private_key)
        
        log.info(f"Adding liquidity for {account.address}")
        log.arrow(f"Adding {amount_a} {token_a} + {amount_b} {token_b}")
        
        # Get token contracts and decimals
        token_a_contract = w3.eth.contract(address=config[f"{token_a.lower()}_address"], abi=ERC20_ABI)
        token_b_contract = w3.eth.contract(address=config[f"{token_b.lower()}_address"], abi=ERC20_ABI)
        
        decimals_a = token_a_contract.functions.decimals().call()
        decimals_b = token_b_contract.functions.decimals().call()
        
        amount_a_wei = int(amount_a * (10 ** decimals_a))
        amount_b_wei = int(amount_b * (10 ** decimals_b))
        
        # Check balances
        balance_a = await get_token_balance(w3, config[f"{token_a.lower()}_address"], account.address)
        balance_b = await get_token_balance(w3, config[f"{token_b.lower()}_address"], account.address)
        
        if balance_a["balance"] < amount_a_wei or balance_b["balance"] < amount_b_wei:
            log.error("Insufficient token balances for liquidity")
            return False
        
        # Approve both tokens
        approval_a = await approve_token(
            w3, config, account,
            config[f"{token_a.lower()}_address"],
            config["liquidity_router"],
            amount_a_wei * 2
        )
        
        if not approval_a["success"]:
            log.error(f"Token {token_a} approval failed")
            return False
        
        approval_b = await approve_token(
            w3, config, account,
            config[f"{token_b.lower()}_address"],
            config["liquidity_router"],
            amount_b_wei * 2
        )
        
        if not approval_b["success"]:
            log.error(f"Token {token_b} approval failed")
            return False
        
        # Add liquidity
        liquidity_router = w3.eth.contract(address=config["liquidity_router"], abi=LIQUIDITY_ROUTER_ABI)
        deadline = int(time.time()) + 20 * 60
        
        log.processing("Adding liquidity...")
        
        liquidity_tx = liquidity_router.functions.addLiquidity(
            config[f"{token_a.lower()}_address"],
            config[f"{token_b.lower()}_address"],
            Web3.to_checksum_address("0x0000000000000000000000000000000000000000"),
            account.address,
            amount_a_wei,
            amount_b_wei,
            int(amount_a_wei * 0.95),  # 5% slippage
            int(amount_b_wei * 0.95),  # 5% slippage
            deadline
        ).build_transaction({
            "from": account.address,
            "gas": 500000,
            "gasPrice": w3.eth.gas_price,
            "nonce": max(approval_a["nonce"], approval_b["nonce"])
        })
        
        signed_tx = w3.eth.account.sign_transaction(liquidity_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for liquidity confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.check(f"Liquidity added successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return True
        else:
            log.error("Liquidity transaction failed")
            return False
            
    except Exception as e:
        log.error(f"Liquidity error: {str(e)}")
        return False

# Convert SUMA to veSUMA
async def convert_to_vesuma(w3, config, private_key, amount, lock_time):
    try:
        account = w3.eth.account.from_key(private_key)
        
        log.info(f"Converting {amount} SUMA to veSUMA")
        log.arrow(f"Lock time: {lock_time} seconds")
        
        # Check SUMA balance
        suma_balance = await get_token_balance(w3, config["suma_address"], account.address)
        amount_wei = int(amount * (10 ** suma_balance["decimals"]))
        
        if suma_balance["balance"] < amount_wei:
            log.error("Insufficient SUMA balance")
            return False
        
        # Approve SUMA
        approval = await approve_token(
            w3, config, account,
            config["suma_address"],
            config["vesuma_address"],
            amount_wei
        )
        
        if not approval["success"]:
            log.error("SUMA approval failed")
            return False
        
        # Create lock
        vesuma_contract = w3.eth.contract(address=config["vesuma_address"], abi=VESUMA_ABI)
        unlock_time = int(time.time()) + lock_time
        
        log.processing("Creating veSUMA lock...")
        
        lock_tx = vesuma_contract.functions.create_lock(amount_wei, unlock_time).build_transaction({
            "from": account.address,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "nonce": approval["nonce"]
        })
        
        signed_tx = w3.eth.account.sign_transaction(lock_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for lock confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.check(f"veSUMA lock created successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return True
        else:
            log.error("veSUMA lock transaction failed")
            return False
            
    except Exception as e:
        log.error(f"veSUMA conversion error: {str(e)}")
        return False

# Stake veSUMA
async def stake_vesuma(w3, config, private_key, amount):
    try:
        account = w3.eth.account.from_key(private_key)
        
        log.info(f"Staking {amount} veSUMA")
        
        # Note: veSUMA balance checking would need specific implementation
        # For now, we'll proceed with the staking transaction
        
        staking_contract = w3.eth.contract(address=config["staking_contract"], abi=STAKING_ABI)
        amount_wei = int(amount * 10**18)  # Assuming 18 decimals
        
        log.processing("Staking veSUMA...")
        
        stake_tx = staking_contract.functions.stake(amount_wei).build_transaction({
            "from": account.address,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address)
        })
        
        signed_tx = w3.eth.account.sign_transaction(stake_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for staking confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.check(f"veSUMA staked successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return True
        else:
            log.error("Staking transaction failed")
            return False
            
    except Exception as e:
        log.error(f"Staking error: {str(e)}")
        return False

# Vote with veSUMA
async def vote_with_vesuma(w3, config, private_key, gauge_address, weight):
    try:
        account = w3.eth.account.from_key(private_key)
        
        log.info(f"Voting with veSUMA")
        log.arrow(f"Gauge: {gauge_address}")
        log.arrow(f"Weight: {weight}")
        
        voting_contract = w3.eth.contract(address=config["voting_contract"], abi=VOTING_ABI)
        
        log.processing("Submitting vote...")
        
        vote_tx = voting_contract.functions.vote(gauge_address, weight).build_transaction({
            "from": account.address,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address)
        })
        
        signed_tx = w3.eth.account.sign_transaction(vote_tx, private_key=account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        log.processing("Waiting for vote confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            log.check(f"Vote submitted successfully! Tx: {config['explorer']}/tx/{tx_hash.hex()}")
            return True
        else:
            log.error("Vote transaction failed")
            return False
            
    except Exception as e:
        log.error(f"Voting error: {str(e)}")
        return False

# Display balances
async def display_balances(w3, config, account_address):
    try:
        log.info("Fetching token balances...")
        
        tokens = ["usdc", "wcbtc", "suma"]
        balances = {}
        
        for token in tokens:
            balance_info = await get_token_balance(w3, config[f"{token}_address"], account_address)
            if balance_info:
                balances[token.upper()] = balance_info
        
        # Create balance table
        table = Table(
            title="[bold cyan]💰 Token Balances[/bold cyan]",
            style="green",
            show_header=True,
            header_style="bold cyan"
        )
        table.add_column("Token", style="white", justify="center")
        table.add_column("Balance", style="green", justify="right")
        table.add_column("Symbol", style="cyan", justify="center")
        
        for token, info in balances.items():
            table.add_row(
                token,
                f"{info['formatted']:.6f}",
                info['symbol']
            )
        
        console.print(table)
        
    except Exception as e:
        log.error(f"Error fetching balances: {str(e)}")

# Automated swap function
async def automated_swaps(w3, config, private_keys, settings):
    successful_swaps = 0
    failed_swaps = 0
    
    try:
        for i in range(settings["transaction_count"]):
            log.info(f"Transaction {i + 1}/{settings['transaction_count']}")
            
            # Select random private key
            private_key = random.choice(private_keys)
            
            # Generate random amount
            amount = generate_random_amount()
            
            # Perform USDC -> WCBTC swap
            success = await perform_swap(w3, config, private_key, "usdc", "wcbtc", amount)
            
            if success:
                successful_swaps += 1
                settings["successful_transactions"] += 1
                
                # Small delay between swaps
                await asyncio.sleep(random.uniform(2, 5))
                
                # Reverse swap: WCBTC -> USDC
                reverse_success = await perform_swap(w3, config, private_key, "wcbtc", "usdc", amount * 0.95)
                
                if reverse_success:
                    successful_swaps += 1
                    settings["successful_transactions"] += 1
                else:
                    failed_swaps += 1
                    settings["failed_transactions"] += 1
            else:
                failed_swaps += 1
                settings["failed_transactions"] += 1
            
            # Update settings
            settings["total_transactions"] += 1
            settings["last_transaction_time"] = datetime.now().isoformat()
            save_user_settings(settings)
            
            # Random delay between transaction rounds
            if i < settings["transaction_count"] - 1:
                delay = random.uniform(10, 30)
                log.info(f"Waiting {delay:.1f} seconds before next transaction...")
                await asyncio.sleep(delay)
        
        # Final summary
        log.check(f"Automation complete! ✓ {successful_swaps} successful, ✗ {failed_swaps} failed")
        
    except Exception as e:
        log.error(f"Automated swaps error: {str(e)}")

# Main function
async def main():
    display_banner()
    
    # Load configuration
    config = load_config()
    w3 = initialize_provider(config)
    private_keys = get_private_keys()
    settings = load_user_settings()
    
    while True:
        try:
            choice = display_menu()
            
            if choice == "1":
                # Start automated swaps
                if settings["transaction_count"] == 0:
                    log.warning("Please set transaction count first (option 2)")
                    continue
                
                log.info("Starting automated swaps...")
                await automated_swaps(w3, config, private_keys, settings)
                
            elif choice == "2":
                # Set transaction count
                try:
                    count = int(console.input("[cyan]Enter transaction count: [/cyan]"))
                    settings["transaction_count"] = count
                    save_user_settings(settings)
                    log.success(f"Transaction count set to {count}")
                except ValueError:
                    log.error("Invalid number entered")
                
            elif choice == "3":
                # Manual swap
                log.info("Manual swap mode")
                token_in = console.input("[cyan]Token in (usdc/wcbtc/suma): [/cyan]").lower()
                token_out = console.input("[cyan]Token out (usdc/wcbtc/suma): [/cyan]").lower()
                
                try:
                    amount = float(console.input("[cyan]Amount: [/cyan]"))
                    await perform_swap(w3, config, private_keys[0], token_in, token_out, amount)
                except ValueError:
                    log.error("Invalid amount entered")
                
            elif choice == "4":
                # Add liquidity
                log.info("Add liquidity mode")
                token_a = console.input("[cyan]Token A (usdc/wcbtc/suma): [/cyan]").lower()
                token_b = console.input("[cyan]Token B (usdc/wcbtc/suma): [/cyan]").lower()
                
                try:
                    amount_a = float(console.input(f"[cyan]Amount {token_a.upper()}: [/cyan]"))
                    amount_b = float(console.input(f"[cyan]Amount {token_b.upper()}: [/cyan]"))
                    await add_liquidity(w3, config, private_keys[0], token_a, token_b, amount_a, amount_b)
                except ValueError:
                    log.error("Invalid amount entered")
                
            elif choice == "5":
                # Convert SUMA to veSUMA
                log.info("Convert SUMA to veSUMA")
                try:
                    amount = float(console.input("[cyan]SUMA amount: [/cyan]"))
                    lock_days = int(console.input("[cyan]Lock days: [/cyan]"))
                    lock_time = lock_days * 24 * 60 * 60  # Convert to seconds
                    await convert_to_vesuma(w3, config, private_keys[0], amount, lock_time)
                except ValueError:
                    log.error("Invalid input entered")
                
            elif choice == "6":
                # Stake veSUMA
                log.info("Stake veSUMA")
                try:
                    amount = float(console.input("[cyan]veSUMA amount: [/cyan]"))
                    await stake_vesuma(w3, config, private_keys[0], amount)
                except ValueError:
                    log.error("Invalid amount entered")
                
            elif choice == "7":
                # Vote with veSUMA
                log.info("Vote with veSUMA")
                gauge_addr = console.input("[cyan]Gauge address: [/cyan]")
                try:
                    weight = int(console.input("[cyan]Vote weight: [/cyan]"))
                    await vote_with_vesuma(w3, config, private_keys[0], gauge_addr, weight)
                except ValueError:
                    log.error("Invalid weight entered")
                
            elif choice == "8":
                # View balances
                account = w3.eth.account.from_key(private_keys[0])
                await display_balances(w3, config, account.address)
                
            elif choice == "9":
                # Transaction history
                log.info("Transaction History")
                console.print(f"[cyan]Total Transactions:[/cyan] {settings['total_transactions']}")
                console.print(f"[green]Successful:[/green] {settings['successful_transactions']}")
                console.print(f"[red]Failed:[/red] {settings['failed_transactions']}")
                console.print(f"[blue]Last Transaction:[/blue] {settings.get('last_transaction_time', 'None')}")
                
            elif choice == "10":
                # Exit
                log.info("Exiting Satsuma DeFi Bot...")
                break
                
            else:
                log.warning("Invalid option selected")
                
        except KeyboardInterrupt:
            log.info("Bot interrupted by user")
            break
        except Exception as e:
            log.error(f"Unexpected error: {str(e)}")
            continue
        
        # Wait before showing menu again
        console.print()
        console.input("[dim]Press Enter to continue...[/dim]")
        console.print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot shutdown complete")
    except Exception as e:
        log.error(f"Fatal error: {str(e)}")
