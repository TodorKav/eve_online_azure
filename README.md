# Eve Online LP Calculator

## Project Description
The **Eve Online LP Calculator** is a web application that allows users to explore all items available for purchase in the LP (Loyalty Point) stores of the universe of **EVE Online**.

The application helps players analyze which items are the most profitable to purchase by calculating the **ISK / LP ratio** and presenting the items ordered by profitability.

---

## Main Functionalities

### LP Store Overview
- Displays all in-game items available in LP stores
- Items are ordered by **profitability (ISK / LP ratio)**

### User Authentication
After authentication, users can:

- Select and add items to a **personal watchlist**
- Organize selected items into **custom tables**
- Move items between tables according to personal criteria

### Watchlist Management
- Create multiple tables for organizing items
- Move and group items based on the user's strategy

### Resource Cost Calculation
- Display all **required resources** needed to obtain selected items
- Calculate the **total cost** of purchasing those resources

---

## Planned Features (To Be Implemented)

### Inventory Check
After authorization, the application will be able to:

- Check which resources the player already owns
- Display which resources **still need to be purchased**

---

## Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/TodorKav/eve_online.git
cd eve_online
pip install -r requirements.txt
python manage.py runserver
Database Setup
The project uses a Supabase database.
Connection credentials are in the env_template.txt file.
Alternative: Local Database
Using a local database is also possible. In this case, you must first run the data fetching scripts located in:
eve/industry/db_fetching_scripts
Before running the scripts, carefully read:
scripts running sequence.md
located in the same folder.

⚠️ Important:
The data fetching process takes approximately 1.5 hours to complete.