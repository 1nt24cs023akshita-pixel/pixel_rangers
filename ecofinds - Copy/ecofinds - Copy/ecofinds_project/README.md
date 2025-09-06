# 🌱 EcoFinds - The Marketplace That Doesn't Cost the Earth

A comprehensive, production-ready sustainable marketplace platform built with Django, featuring AI-powered verification, gamification, and multi-language support.

## 🎯 Core Concept

**EcoFinds** is a revolutionary second-hand marketplace that promotes sustainable consumption through:

- **Smart Pricing**: AI-powered pricing suggestions based on market data
- **Sustainability Tracking**: CO2 savings calculation and environmental impact metrics
- **Gamification**: Eco levels, challenges, and badges to encourage sustainable behavior
- **AI Verification**: Fake image detection and abuse prevention
- **Multi-language Support**: Global accessibility with translation services
- **Trust & Safety**: Comprehensive chat system with abuse detection

## 🚀 Key Features

### 🛍️ **Core Marketplace**
- User authentication with email-based login
- Product listing with image/video upload
- Smart pricing calculator
- Advanced search and filtering
- Shopping cart and checkout
- Order management and history

### 🌱 **Sustainability Features**
- CO2 savings calculation per transaction
- Environmental impact tracking
- Eco badges and levels (Apprentice → Ninja → Legend)
- Monthly sustainability challenges
- Shareable sustainability score cards

### 🤖 **AI-Powered Features**
- Fake image detection
- Abuse detection in chat messages
- Smart pricing suggestions
- Product verification
- Automated content moderation

### 🌍 **Accessibility & Inclusivity**
- Multi-language support (20+ languages)
- Mobile-first responsive design
- Low bandwidth optimization
- Currency conversion
- Localized content

### 🎮 **Gamification**
- Eco points system
- Achievement badges
- Leaderboards
- Monthly challenges
- Social sharing features

## 🛠️ Tech Stack

### **Backend**
- **Django 5.2.6** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database
- **Redis** - Caching and message broker
- **Celery** - Background task processing

### **AI & ML**
- **TensorFlow** - Machine learning models
- **OpenCV** - Image processing
- **scikit-learn** - Data analysis
- **Custom AI services** - Image verification, abuse detection

### **Frontend**
- **Bootstrap 5** - UI framework
- **FontAwesome** - Icons
- **JavaScript** - Interactive features
- **Responsive design** - Mobile-first approach

### **Infrastructure**
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Gunicorn** - WSGI server
- **AWS S3** - File storage
- **Prometheus + Grafana** - Monitoring

## 📦 Installation

### **Prerequisites**
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### **Local Development**

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ecofinds.git
cd ecofinds
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp env.example .env
# Edit .env with your configuration
```

5. **Set up database**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Run development server**
```bash
python manage.py runserver
```

### **Production Deployment**

1. **Using Docker Compose**
```bash
docker-compose up -d
```

2. **Manual deployment**
```bash
# Set production settings
export DJANGO_SETTINGS_MODULE=ecofinds_project.settings_production

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn ecofinds_project.wsgi:application
```

## 🔧 Configuration

### **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `EMAIL_HOST` | SMTP server for emails | Yes |
| `AWS_ACCESS_KEY_ID` | AWS S3 access key | For production |
| `AI_IMAGE_DETECTION_API_KEY` | AI service API key | Optional |
| `GOOGLE_TRANSLATE_API_KEY` | Translation service key | Optional |

### **Database Setup**

```sql
-- Create database
CREATE DATABASE ecofinds;
CREATE USER ecofinds WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecofinds TO ecofinds;
```

## 📱 API Documentation

### **Authentication**
```bash
# Register user
POST /api/auth/register/
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword"
}

# Login
POST /api/auth/login/
{
    "email": "john@example.com",
    "password": "securepassword"
}
```

### **Products**
```bash
# List products
GET /api/products/?search=laptop&category=electronics&min_price=100

# Create product
POST /api/products/
{
    "title": "MacBook Pro 2020",
    "description": "Excellent condition...",
    "category_id": 1,
    "condition": "excellent",
    "price": 1200.00,
    "original_price": 2000.00
}
```

### **Cart & Orders**
```bash
# Add to cart
POST /api/cart/add/{product_id}/

# Checkout
POST /api/checkout/

# Get orders
GET /api/orders/
```

## 🎮 Gamification System

### **Eco Levels**
- **Eco Apprentice** (0-999 points): New to sustainability
- **Eco Ninja** (1000-4999 points): Committed to green living
- **Eco Legend** (5000+ points): Sustainability champion

### **Earning Points**
- List a product: +10 points
- Complete a purchase: +25 points
- Save 1kg CO2: +5 points
- Complete challenge: +100 points
- Get positive review: +15 points

### **Badges**
- **Trusted Recycler**: List 10+ products
- **Eco Warrior**: Save 100kg CO2
- **Community Builder**: Help 5+ users
- **Green Champion**: Complete 3 challenges

## 🌍 Multi-language Support

Supported languages:
- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean, Chinese
- Arabic, Hindi, Bengali, Tamil, Telugu
- Malayalam, Kannada, Gujarati, Marathi, Punjabi

## 🤖 AI Services

### **Image Verification**
- Detects AI-generated images
- Verifies product authenticity
- Prevents fake listings

### **Abuse Detection**
- Monitors chat messages
- Filters inappropriate content
- Protects user safety

### **Smart Pricing**
- Market analysis
- Condition assessment
- Competitive pricing suggestions

## 📊 Monitoring & Analytics

### **Metrics Tracked**
- User engagement
- Transaction volume
- CO2 savings
- System performance
- Error rates

### **Dashboards**
- Grafana: System metrics
- Django Admin: Business metrics
- Custom: Sustainability impact

## 🔒 Security Features

- **Authentication**: Email-based login with 2FA support
- **Authorization**: Role-based access control
- **Data Protection**: GDPR compliant
- **Rate Limiting**: API abuse prevention
- **Content Security**: XSS and CSRF protection
- **File Upload**: Secure image/video handling

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Performance Optimization

- **Database**: Optimized queries with select_related/prefetch_related
- **Caching**: Redis-based caching for frequently accessed data
- **CDN**: Static file delivery via AWS CloudFront
- **Image Optimization**: Automatic resizing and compression
- **Lazy Loading**: Efficient data loading strategies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Bootstrap team for the UI components
- FontAwesome for the icons
- All contributors and testers

## 📞 Support

- **Documentation**: [docs.ecofinds.com](https://docs.ecofinds.com)
- **Issues**: [GitHub Issues](https://github.com/yourusername/ecofinds/issues)
- **Email**: support@ecofinds.com
- **Discord**: [EcoFinds Community](https://discord.gg/ecofinds)

---

**Made with 🌱 for a sustainable future**
