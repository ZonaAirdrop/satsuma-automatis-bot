# 🥷 Satsuma Automation Bot 

**Satsuma Automation Bot** is a Python bot designed to automate interactions with the [Satsuma](https://satsuma.xyz) platform.  
With features like auto-swapping, staking, voting, and transaction history, it’s perfect for DeFi users looking for high efficiency.

---

## 🚀 Main Features

1. ✅ **Start Automated Swaps** – Perform automatic token swaps.  
2. 🔢 **Set Transaction Count** – Define the number of transactions per wallet.  
3. 💱 **Manual Swap** – Perform a manual token swap.  
4. ➕ **Add Liquidity** – Add liquidity to the pool.  
5. 🔄 **Convert SUMA to veSUMA** – Convert SUMA tokens to veSUMA.  
6. 📥 **Stake veSUMA** – Stake veSUMA tokens for voting power.  
7. 🗳️ **Vote with veSUMA** – Vote directly through the bot.  
8. 📊 **Show Balances** – Display wallet balances.  
9. 📜 **Transaction History** – View wallet transaction history.

---

## 📦 Requirements

- Python 3.9 or newer  
- Pip (Python package manager)

---

## 📥 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ZonaAirdrop/satsuma-automatis-bot.git
cd satsuma-automatis-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> If `requirements.txt` is missing, you can install manually:

```bash
pip install web3 aiohttp eth_account colorama pytz
```

---

## 🔐 Environment Setup (.env)

For security, wallet private keys are stored in a `.env` file.  
Create a `.env` file in the root directory and add:

```env
PRIVATE_KEY_1=0x28658a8399abcdef1234567890ab
PRIVATE_KEY_2=0xabcdefabcdefabcdef...
```

- You can add as many keys as you want: `PRIVATE_KEY_3`, `PRIVATE_KEY_4`, etc.  
- Format must be valid (start with `0x`).

> ⚠️ **NEVER upload your `.env` file publicly!** Make sure to include it in your `.gitignore`.

---

## ▶️ Run the Bot

```bash
python bot.py
```

Follow the interactive prompts in the terminal and select the desired feature.

---

## 📁 Project Structure

```
satsuma-automatis-bot/
├── bot.py             # Main bot script
├── .env               # Stores private keys
├── wallets.txt        # (optional) additional wallets
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## 🔐 Security

> ⚠️ **IMPORTANT:**  
> Never share your private keys!  
> Use a `.env` file and run the bot only in a secure environment.

---

## 🌐 Community & Support

Join our Telegram community for updates, support, and discussions:

👉 [t.me/ZonaAirdr0p](https://t.me/ZonaAirdr0p)

---
