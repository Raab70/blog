## Long Term Support for Data APIs

In our recent episode on [The Data Refuge Project](https://dataskeptic.com/blog/episodes/2017/the-data-refuge-project), guest [Margaret Janz](https://twitter.com/MargaretJanz) shared many reasons why data can disappear.  An embarassing picture from one's youth posted to the internet can make a person feel as though information is permanent and difficult to erase.  It's a useful exercise to consider the consequences of information being permanent before posting to the internet, the reality, information is quite fragile.

Certain organizations like [archive.org and their Wayback Machine](https://archive.org/) seek to preserve this history of the internet.  Their collection is vast, and their mission seems to focus on storing everything.  The cost of storage continues to shrink.  Even if, in the future, archive.org found it impossible to keep their entire history, surely the discussion about what would need to be selectively deleted to free space would be a highly scrutinized discussion.  Although they may not crawl every page, once crawled, they seem committed to having no preference for one page over another.

Sharing via massive systems like Twitter is another good way of ensuring some degree of permanence.  Even if it falls out of popularity, even if it ceases continued operation, surely the archive of all tweets will be a curiosity that the Library of Congress and other organizations may attempt to capture and preserve.  Similarly, many people share my opinion that Wikipedia is an absolute treasure of our time.  If a series of global disasters occured, I imagine many people's first thought for long term preservation would be getting a backup of the Wiki persisted to some media that offers a long term likelihood of surviving without physical degregation to the media.  Rome didn't last forever, and on the epoch scale, its a bit difficult to speculate what will and will not survive.

However, when leaving the canopy made by the mightest of services and systems in the digital forest, a constant churn of saplings can be found.  Small systems that are useful to subsets of the population, do have a high risk of ceasing operations and destroying a wealth of data.

Sites like archive.org only capture of fraction of the total internet.  They don't archive pages requiring a login.  They don't archive data which can only be viewed by conducting a search of some kind, or POSTing a form to a website.  They presumably don't archive "exotic" files available for download either.  As Margaret mentioned in the interview, Data Refuge archives some data that fits into this broader category, but even here, there are limits.

Further, sites and services that are backing up data are only backing up, by definition, the data.  What happens to sites that provide data via API, which consumers call on demand?  These systems, while useful services, encourage the user to consume on demand.  This means the consumers aren't necessarily helping create redundant copies.  Granted, consumers might keep some amount of local cache, but almost by design, they won't have a complete backup.  If an API disappears, the data is exposed is gone.  Yes, there's some possibility the consumers of the API could rally together and share their caches in an attempt to rebuild the full dataset, but there's no assurances.  Further, many APIs will put tight restrictions on just how much can be cached.  This might be due to a revenue model charging for individual calls, or maybe simply be a best practice due to the dynamic nature of the responses provided.

I'm reminded of a service formerly found at http://stats.grok.se.  This site provided some useful data about Wikipedia pageviews.  I had been building a tool for the [Guerrilla Skepticism on Wikipedia](http://guerrillaskepticismonwikipedia.blogspot.com/) project which relied on this datasource.  Then one day, it disappeared!

I'm sure if I had been checking that project's main site, I might have seen some announcement.  But after finishing and testing the software I intended to create, I had hoped I could ride away into the sunset having left behind a tool for the GSoW team to use.  The disappearance of this API effectively killed the tool I was working on.

In the end, thanks to some pointers from [Tim Farley](https://skeptools.wordpress.com/), I discovered that Wikipedia had launched a more official version of this service.  If I dug into the background, I imagine I'd find out that grok.se discontinued their service in favor of the one released by Wikimedia.  As far as I know, there was no announcement list that I could have subscribed to warning me of the pending termination of service and pointer to the new service.  That's a lesson to API creators and consumers.

In my case, we were lucky.  The discontinued service had a new one that, while not a direct replacement, was easy to refactor to work with.  The project for GSoW is back up and running.  However, this incident made me think hard about how these services might be maintained in a more robust, decentralized way.

I think there are three possible paths that could be explored toward better permanence of microservices like this one.

First, creators of such services should consider uploading them to the merging set of algorithmic marketplaces.  Granted, one has to hope that those marketplaces themselves don't disappear or change their services in a breaking fashion.  However, if these marketplaces do manage to stay in existance, they'll likely outlive the maintainers of smaller microservices.  A standardized format and perhaps some federation could yield some best practices that allowed containerized services to migrate smoothly.

Second, I think an economic solution could be greated.  What if APIs were designed to run on AWS infrastructure which had a special sort of financing account.  Whenever fees were incurred, AWS could deduct those charges from the account.  If the account balance is emptied, AWS would simply start throwing exceptions instead of returning results.  Smarter financing like annuities could be employed.  An annuity is (essentially) a lump sum of money for which one tries to only spend the interest, while possible re-investing some of that interest in principle.  If I wanted my API service to live forever, wouldn't it be cool if I could create an annuity for it in this fashion?  If the interest earned last month is consumed with AWS fees, the API throws errors for the rest of the month.  That is, unless a consumer decides to make a one time donation, reinvigorating it for the balance of their donation.

Third and finally, I'd love to see a proposal for how services like this could be federated and do data sharing with something like Torrents.  What if API services were kept afloat by the contributions of seeders who value the service?

All too often, I see very well intentioned open source services come and go because there were no long term plans.  It would be fantastic if we lived in a world where frictionless options were available to allow people to preserve their services on a containerized platform.  I hope these thoughts might inspire people to think more about these problems, and perhaps commentors to share stories they know about preserving useful services.