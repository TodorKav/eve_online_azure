# To avoid potential conflicts, it is recommended to run the files in the folder in this order:

---
1. categories.py
2. groups.py
3. market_groups.py
4. types.py or tasks.py (both files contain the same code, but tasks.py uses Celery and Redis to allow concurrent data fetching, which drastically reduces the time needed to fetch all data. However, it requires additional setup of Celery and Redis.)
5. corporations_with_lp_stores.py
6. Corporations_lp_item_types
7. market_prices.py

---
### Recommended updates for each model:

| Model                       | Period            |
|-----------------------------|-------------------|
| Categories                  | every 3–6 months  |
| Groups                      | every 3–6 months  |
| Corporations_with_lp_stores | every 3–6 months  |
| Corporations_lp_item_types  | every 3–6 months  |
| MarketGroups                | mounthly          |
| Types                       | mounthly          |
| Market prices               | hourly            |

#### Run all after expansions/patches.
