# PTT Scraper README

## Introduction
This code allows you to scape PTT (a popular forum in Taiwan) on the board of your choice with keyword(s) within a particular time range of your choice. 

## Operations
1. Download and open the code
2. Modify the keyword, board, begin and end date you want to search
Example:
![Screen Shot 2023-11-27 at 1.23.17 PM](https://hackmd.io/_uploads/SJsAOYMra.png)
If you don't want to search for a certain range of time (i.e., if you want to scrape for all pages), leave the begin and end dates empty strings, like: `""`, and set the `start_page` in`getmsg()` to **-1**。
3. If you know the exact page you want to start scraping, you may modify the `start_page` directly in `getmsg()`. Also, don't forget to change the argument in the `for loop` in the next line. (Note that the search begins from thousands and ends in 0)


## Outputs
For easier text process later on, there will be two types of output files.
#### File 1: Main Content for all articles 
* File name
    * *ppt{board}_{keywords}{last_scraped_page}.csv*
* Columns
    * 標題
    * 作者
    * 時間
    * 看板
    * 超連結
    * 內文

#### File 2: Pushes
* File names 
    * *ppt{board}Push{content_id}.csv*
* Columns
    * tag
    * userID
    * date
    * time
    * content & pushIP

Each `push file` contains all the pushes in one article. The `id` of an article is identified from the last chunk of its URL. Once an article is identified, a push file will be created as long as any content is found in the push area.
