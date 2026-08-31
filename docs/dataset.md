# Dataset Methodology

To train and evaluate the Catalog-SLM model, a structured synthetic dataset containing diverse bilingual product descriptions was generated. This approach allows complete control over the representation of target attributes and ensures that the model learns the relevant domain terminology.

## Dataset Composition

The dataset comprises **2,122 unique product descriptions** mapped across three linguistic distributions:
- **English (en)**: Descriptions structured using standard English terms (e.g., "Black Nike running shoes for men, size 9").
- **Hindi (hi)**: Descriptions in pure Hindi written in Devnagari script (e.g., "पुरुषों के लिए लाल सूती शर्ट").
- **Mixed / Hinglish**: Descriptions that blend English attributes and Hindi connective structures (e.g., "लाल रंग की cotton shirt men's size M").

## Target Classification Taxonomy

Each sample is labeled with target indices corresponding to 10 distinct prediction tasks:

| Target Head | Number of Classes | Example Classes |
| :--- | :--- | :--- |
| **Category** | 5 | Clothing, Footwear, Electronics, Accessories, Home & Kitchen |
| **Subcategory** | 27 | T-Shirts, Shirts, Jeans, Running Shoes, Smart Watches, Wallets, Cookware, etc. |
| **Product Type** | 27 | T-Shirt, Shirt, Jeans, Running Shoes, Smart Watch, Wallet, Cookware, etc. |
| **Color** | 10 | Red, Blue, Green, Black, White, Yellow, Grey, Pink, Brown, None |
| **Material** | 9 | Cotton, Leather, Denim, Polyester, Plastic, Metal, Ceramic, Glass, None |
| **Gender** | 6 | Men, Women, Boys, Girls, Unisex, None |
| **Size** | 12 | S, M, L, XL, XXL, 6, 7, 8, 9, 10, 11, None |
| **Brand** | 10 | Nike, Adidas, Puma, Samsung, Apple, Philips, Prestige, Milton, Tommy Hilfiger, None |
| **Quantity** | 6 | 1, 2, 3, 4, 5, None |
| **Language** | 3 | English, Hindi, Mixed |

## Data Formatting & Split

The text corpus undergoes vocabulary building where unique tokens are mapped to integers. The samples are padded to a max sequence length of 20 words. 

The dataset is divided using a fixed random seed (42) to prevent data leakage:
- **Training Set (80%)**: 1,697 samples.
- **Validation Set (10%)**: 212 samples.
- **Test Set (10%)**: 213 samples.
