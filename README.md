# HCI Chatbot
## Rationale
Our goal for this project is to create a functional chatbot to assist new students by addressing their queries about the school. Inspired by ChatGPT, we aim to develop a specialised chatbot that excels in answering HCI-related questions on Discord, aiding both freshmen and seniors in understanding the school.

## Installation
```
pip install -r requirements.txt
```
**All other required files will be automatically installed after running code**
## Files

### `src/bot/main.py`
Main driver code for running The Orientator Discord Bot. Requires `src/bot.json`, which contains `{"token" : TOKEN}`, `TOKEN` being the API Token for the Discord Bot.

#### Command : `?date`
#### Command : `Create Conversation`

### `src/bot/query_response.py`
Separate code called by `src/bot/main.py` for chatbot capabilities.

### `src/bot/get_isp_events.py`
Separate code called by `src/bot/main.py` for retrieving ISP events. Requires `src/data/isp_events.json`.

### `src/data/base_data.csv`
Original data for chatbot, unedited and in simplest form. Required for training chatbot. Contains ~81 rows of data.

### `src/data/augmented_data.csv`
Augmented data for chatbot, changed and complex form. Required for training chatbot. Contains ~6700000 rows of data. Created after running `src/data-collection/augment_data.py`.

### `src/data/processed_data.csv`
Augmented and processed data for chatbot, changed and final form. Required for training chatbot. Contains ~2000 rows of data. Created after running `src/data-collection/augment_data.py`.

### `src/data/isp_events.json`
Original data for ISP events, required for `?date` command. Created after running `src/data-collection/scrape_isp.py`.

### `src/data-collection/augment_data.py`
Separate code for augmenting data. Required for training chatbot. Requires `src/data/base_data.csv`. 

### `src/data-collection/scrape_isp.py`
Separate code for web scraping ISP-HS. Required for `src/bot/get_isp_events.py` and `src/data/isp_events.json`. 

### `src/model/train_model.ipynb`
Main code for training chatbot model. Requires `src/data/base_data.csv`, `src/data/augmented_data.csv`.

### `src/model/test_model.py`
Separate code for quick testing of online models (on HuggingFace), or local models (stored in folder). 

## Others (To create on your own)
### `src/.env`
Contains directory information (required)

`PARENT_DIR` = Full path to `The-Orientator-PW-2023/` folder

`EXECUTABLE_PATH` = Path to `src/data-collection/drivers/chromedriver.exe`

### `src/bot.json`
Contains Discord Bot API Token

`"token"` : Discord Bot API Token

### `src/isp_cookies.json`
Contains cookies for ISP-HS login (requires HCI account)

1. Install `Cookie Editor` extension from Chrome Web Store
2. Log into ISP-HS in browser
3. Press on `Cookie Editor` extension in the top-right corner of screen
4. Export Cookies as JSON (copied to clipboard)
5. Create `src/isp_cookies.json` and paste JSON into file