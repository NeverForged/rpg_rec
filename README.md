# Role Playing Game Recommender
Purpose of this project is to make a recommender for table-top role playing games (rpgs) in order to accomplish two goals:
1. Get more experience using spark and making recommenders
2. Determine what is happening in the industry for a personal project, "Neverforged".
Spark experience, and other experience with large data, is crucial in the workplace of today.  I am starting off with [a tutorial on making movie recommenders](https://www.codementor.io/jadianes/building-a-recommender-with-apache-spark-python-example-app-part1-du1083qbw) and working my way up to more complex ideas.

## Data Understanding
So, there is a slight issue with my plans: I want to make a recommender for RPG *systems*, but have decided to grab data based on RPG *products*, namely the ratings and reviews found at [DriveThruRPG.com](http://www.drivethrurpg.com/).  So one of my main hurdles is to convert
rating data from individual products into a system of rating the game behind the products.  
For those unfamiliar with table-top RPGs, the basic idea is this:
* There are a number of systems/games out there (usually with multiple editions of each)
* Each *system* has some number of products; for example, the *"original"* rpg, *Dungeons & Dragons*, typically has three main books: the *Player's Handbook*, the *Dungeon Master's Guide*, and some sort of *Monster Manual*.  On top of this, there are a number of other supplements: options for players, equipment expansions, adventures/stories, etc.
* I want to recommend a *system* based on how users of [DriveThruRPG.com](http://www.drivethrurpg.com/) rated the various pdf supplements (usually adventures and non-main books) that they downloaded/purchased.

Seems daunting, but I made a few assumptions:
* Customers only buy products for games they are interested in.
* The more products reviewed, the more interest the customer has in that system.
* A negative review of a *product* is still an endorsement of a *system*; in fact, one could argue that you wouldn't care about a bad *product* if you didn't like the system.  This assumption improves with higher numbers of reviews (since one bad product clearly did not turn them off of the system).

So my goal is to use the number of reviews of a given system's products as an implicit rating of the game itself.  Clearly normalization must be done to justify this.

## First Spark Attempt
My first instinct was to use [Spark ALS](https://github.com/NeverForged/rpg_rec/blob/master/source/SparkRPGRecommender.ipynb). This came out okay (not great), but I noticed two things:
1. I don't know enough about recommenders to set the *regularization_parameters* (yet) and
2. This was running on my Laptop locally... apparently 17,688 data points is not enough to justify using Spark on an EC2 as I originally thought I would have to do.

## Building A Recommender From Scratch
To gain a better understanding of how recommendation systems work, I decided to [build one from scratch](https://github.com/NeverForged/rpg_rec/blob/master/source/Recommender.ipynb).  This uses collaborative filtering and cosine similarity to build a recommendation model.  Removing 20% of my users at random and testing on them gave an RSME of 0.182 and a maximum error of 5... not great, but not terrible.  Of course, none of the fun regularization stuff was used (yet), so still not expecting great things.

## Non-Negative Matrix Factorization
