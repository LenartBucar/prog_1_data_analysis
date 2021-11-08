# prog_1_data_analysis

This is a project for my Programming 1 class. 

In this project I will analyse few thousand best selling games from the online platform [Steam](https://store.steampowered.com/search/?filter=topsellers&page=1).

For each game I will collect the following data:

* Name of the game
* Release date
* Genres of the game
* Number of all reviews and the amount of positive reviews
* Number of recent reviews and the amount of positive reviews
* Developer and publisher
* Price of the game
* Languages supported
* Bundles in which the game is available
* Available additional content for the games
* ~~Most recent announcements~~ *most games don't have that, so this was dropped*
* Game attributes
* Age rating
* ~~Game awards and~~ external scores
* Minimum and reccomended system requirements

A few of the questions I will try to answer are:

* Is there a corelation between the price of the game and its publishers?
* Which developers/publishers have the best rated games? ~~The most awarded games?~~ 
* Are people more likely to review expensive games?
* ~~Do reviews of the game tend to change if there is a recent announcement?~~
* Are more demanding games also more expensive? Are the games that support more languages more expensive? Better rated?

## Data files

The `.csv` files are located in [their folder](parser/CSV). The contents of the files are as follows:
* [entities](parser/CSV/entities.csv) - internal ID and name of the developer/publisher. 
* [game data](parser/CSV/game_data.csv) - main information about each game
* [game info](parser/CSV/game_info.csv) - contains tags for the games. `T` means user tags, `C` means content tags, and `R` means rating tags
* [game languages](parser/CSV/game_languages.csv) - contains the languages the game supports. The three booleans represent the support for interface, subtitles, and audio in that order
* [game price](parser/CSV/game_price.csv) - contains name of the purchase option, discount, base price, and discounted price. `M` implies main option while `D` stands for DLC
* [game reviews](parser/CSV/game_reviews.csv) - contains reviews for the games
* [game sysreq](parser/CSV/game_sysreq.csv) - system requirements for the games, `M` standing for minimum and `R` for recommended. 