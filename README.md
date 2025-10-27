# 🚀 AidLedger - Transparency in Aid Distribution

**AidLedger** is a blockchain-powered transparency platform that allows NGOs, donors, and beneficiaries to track donations and aid distribution on Hedera Hashgraph. The system ensures trust, accountability, and transparency in how aid funds move from donors to final recipients.

## 🌟 Features

- **🔗 Hedera Integration**: Built on Hedera Hashgraph for fast, secure, and sustainable blockchain operations
- **📝 HCS Logging**: All transactions are immutably logged on Hedera Consensus Service
- **🪙 Tokenization**: AidCoin token for representing aid funds using Hedera Token Service
- **🔍 Transparency**: Real-time verification of transactions via Hedera Mirror Node API
- **📊 Dashboard**: Beautiful web interface for tracking donations and distributions
- **🔌 REST API**: Complete API for integration with other systems

## 🛠️ Tech Stack

- **Backend**: Django 4.2.7 + Django REST Framework
- **Blockchain**: Hedera Hashgraph (HCS + HTS)
- **Database**: PostgreSQL
- **Frontend**: Django Templates + Bootstrap 5
- **SDK**: Hedera SDK for Python

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Hedera Testnet Account (get one at [portal.hedera.com](https://portal.hedera.com))

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd AidLedger

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file with your Hedera credentials:

```env
# 🌟 AIDLEDGER HEDERA CONFIGURATION
# Get these from portal.hedera.com

# 🔐 Operator Credentials
OPERATOR_ID=0.0.7124405
OPERATOR_KEY=302e020100300506032b65700422042058cd811e4ffc35acac0a84f84f90646317bf99b0e0889ef1a0927d44daf5e48c

# 📝 Transparency Topic (HCS) - Will be created automatically
TOPIC_ID=0.0.7139041

# 🪙 AidCoin Token (HTS) - Will be created automatically
TOKEN_ID=0.0.7139042

# 🌐 Network Configuration
HEDERA_NETWORK=testnet
HEDERA_CHAIN_ID=296

# 💰 Default Transaction Fees (in HBAR)
MAX_TX_FEE=2
MAX_QUERY_PAYMENT=1

# 🔒 DJANGO SETTINGS
DEBUG=True
DJANGO_SECRET_KEY=django-insecure-aidledger-2024-hedera-blockchain-charity
ALLOWED_HOSTS=localhost,127.0.0.1

# 🗄️ DATABASE CONFIGURATION
DATABASE_NAME=aidledger_db
DATABASE_USER=postgres
DATABASE_PASSWORD=password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb aidledger_db

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Initialize Hedera Services

```bash
# Initialize HCS topic and AidCoin token
python manage.py init_hedera

# Seed with sample data
python manage.py seed_data
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to see the AidLedger dashboard!

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats/` | GET | Get AidLedger statistics |
| `/api/donate/` | POST | Create new donation |
| `/api/distribute/` | POST | Create new distribution |
| `/api/transactions/` | GET | Get all transactions |
| `/api/verify/{txn_hash}/` | GET | Verify transaction on Hedera |
| `/api/donors/` | GET/POST | List/create donors |
| `/api/ngos/` | GET/POST | List/create NGOs |
| `/api/recipients/` | GET/POST | List/create recipients |

### Example API Usage

#### Create a Donation

```bash
curl -X POST http://localhost:8000/api/donate/ \
  -H "Content-Type: application/json" \
  -d '{
    "donor_id": 1,
    "ngo_id": 1,
    "amount": "1000.00"
  }'
```

#### Create a Distribution

```bash
curl -X POST http://localhost:8000/api/distribute/ \
  -H "Content-Type: application/json" \
  -d '{
    "ngo_id": 1,
    "recipient_id": 1,
    "amount": "500.00"
  }'
```

#### Verify Transaction

```bash
curl http://localhost:8000/api/verify/0.0.123456@1640995200.123456789/
```

## 🏗️ Architecture

### Core Components

1. **Django Models**
   - `Donor`: Donor information and wallet
   - `NGO`: NGO details and wallet
   - `Recipient`: Beneficiary information
   - `Donation`: Donor → NGO transactions
   - `Distribution`: NGO → Recipient transactions

2. **Hedera Integration**
   - **HCS (Consensus Service)**: Immutable transaction logging
   - **HTS (Token Service)**: AidCoin token management
   - **Mirror Node API**: Transaction verification

3. **REST API**
   - Django REST Framework
   - Serializers for data validation
   - ViewSets for CRUD operations

4. **Frontend Dashboard**
   - Bootstrap 5 responsive design
   - Real-time statistics
   - Transaction history
   - Hedera integration status

## 🔧 Management Commands

```bash
# Initialize Hedera services
python manage.py init_hedera

# Seed sample data
python manage.py seed_data

# Run Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Settings

1. Set `DEBUG=False` in production
2. Use environment variables for sensitive data
3. Configure proper database credentials
4. Set up static file serving
5. Configure CORS for your domain

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Hedera Hashgraph](https://hedera.com/) for the blockchain infrastructure
- [Django](https://djangoproject.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the UI components

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [Hedera Documentation](https://docs.hedera.com/)
- Join the [Hedera Community](https://hedera.com/discord)

---

**Built with ❤️ for humanitarian aid transparency**
