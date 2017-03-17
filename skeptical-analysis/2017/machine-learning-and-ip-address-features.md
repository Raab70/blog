## Machine Learning and IP Address Features

A frequent use case for applying machine learning is predicting some outcome based on Internet traffic.  Although some effort is required, a well formated web server log can provide a wealth of raw data to be transformed into useful features for learning.  Every company with an internet presence has a web server.  With the exception of high security sites that make a point of *not* logging, these relatively compact text files are often managed through log rotation that moves the history to a persistent store (S3 being a popular choice) where they are (relatively) inexpensive to keep and may live for a very long time without threat of archiving for space.

In the absence of better telemetry being available, a data scientist may often need to start with the processing of those logs, and if they are lucky, mine for insights captured in the debugging messages written semi-absent mindedly by software developers as well as the details captured by the web server itself.  Sessions for linking activity can help extract descriptions of actions taken on the site.  Things like the user agent string could possibly reveal weak predictors.  The IP address of the visitor can be looked up in 3rd party systems, retrieving otherwise unavailable metadata such as approximate geographic area, residential or commercial source, and potentially other datapoints.

In my experience, data derived from IP often proves to be helpful, but never dramatically so.  On one had, perhaps I haven't been exposed to the right problem for which IP data admits a good solution.  However, I'm willing to wager that in reality, IP address metadata is, at best, a low resolution measurement tool.

Yet, time and again, I've seen it provide *some* predictive power.  Often, this relates to whether or not the user has a history of requests from this known IP address (a strong indicator of valid user behavior).  The more interesting case, of course, is users logging in from an unexpected IP address.  Dinstinguishing between a stolen account and a person on vacation can be pretty tricky, however.  There are also cases of people sharing accounts with friends and relatives.  While that might be explicitly forbidden in the user agreement, its something companies often have to make difficult operational choices regarding just how much they want to police it.  If you pursue me because my brother and I share some account, is that going to lead to him signing up (+1 account) or me indignantly cancelling (-1 account)?

In my experience, IP address metadata is a useful, but not dominantly useful feature.  The problems I've worked on for the companies I've had the pleasure of helping in my career have consistently reached a point where we must debate precision and utility.  Generally, continuing to improve a model would likely yield improvements.  Depending on the revenue related to the system being improved, the investment of effort might not be worth it.  A 0.01% accuracy improvement is definitely worth pursuing for some businesses.  However, the additional revenue earned for small and medium enterprises might be on par or less than what it would cost to get that 0.01% improvement, which indicates it's probably a good time to stop working on the problem.

So I've never been in a position where I made a recommendation that I dive deeper into IP address metadata, but I recently faced this problem again.  I had to make a judgement call about whether or not I should recommend to a company that they continue to invest my time exploring more effective ways to leverage IP address data.  There are a few additional steps I do need to take which will be valuable, but ultimately, I'm going to recommend the client put a limit on my time in this regard very soon.  But I also need to justify it.

Let's take a hypothetical.  What if one one-hundreth of a percent improvement in accuracy represented a million dollars revenue annually?  Full speed ahead!  What would I do if I found myself in that situation?

I immediately thought of a few pitfalls related to IP metadata that I thought would be interesting to mention here.  If I don't explore these considerations, the situations described below would wind up as noise in my models, bounding the full potential of their accuracy by a nominal amount.  What are some things I might better represent during feature engineering?

The first thing that comes to mind is special case handling of [Tor](https://www.torproject.org/download/download-easy.html.en) nodes.  If you're not familiar with the so called "onion router", you can read about it in many places.  The basic idea is that users all contribute some amount of their bandwidth, and Tor routes traffic through a network of distributed, unrelated places in a (hopefully) anonymous fashion such that identifying the source of the traffic is difficult if not impossible.

Tor is an important technology.  We all have a right to privacy on the internet.  While my "secrets" might amount only to some embarassing guilty pleasures, other people deal with more major stakes.  Regardless of the reasons, Tor is a reality, and people do use it.  Sometimes, they show up in the webtraffic data scientists want to study.  By definition, their user behavior is going to look a bit unusual.

There exist people who assume the use of more advanced privacy tools like Tor is only done by users commiting some sort of crime.  I've heard people ask the specious question: what's the harm in mis-classifying a criminal in your model?  Indeed, bad actors do use Tor, but so do good actors.  Traffic from a wide variety of disparate IP addresses is something worth scruitinizing.  Abusive or criminal behavior might indeed have this signature, but not reliably.  There exist many situations where a "good" user elects to use tools like Tor and are interacting with a company's products or services in perfectly legitimate and encouraged ways.

My conclusion with regard to tools like Tor is that it would be useful to develop a feature in a model such as `isTorUser` but to not attempt to bias the model in any way.  If a machine learning algorithm finds this to be a discriminative feature useful in making predictions (probably in combination with other features), that's great.  If the algo ignores this feature, that's effective too.

What about changes in IP addresses?  Most ISPs do not offer a static IP to customers.  Other ISPs offer this only at a premium.  For most consumers, this option is of little or no value.  In my own life, I gave up paying extra for a static IP about 10 years ago when I stopped hosting any servers on my home premises.  At first I made the investment in a dedicated rack mount machine, but have since naturally moved to entirely virtualized cloud services.  The idea of having a physical server in my actual home feels deeply foolish to me today in 2017.  As a result, I no longer care about having a static home IP.  Although incidentally, I've noticed that most ISPs. while not guarenteeing me a static IP, do tend to issue me one in practice.

But I suppose there must be somewhere in the world where ISPs actually do rotate IP addresses around a bit.  If you're counting the number of different users identified with a particular IP, or annotating IP addresses as having had "bad behavior" in the past, those features might not be useful.  If a bad user has their IP rotated away and coincidentally assigned to a good user, you really wouldn't want them inheriting the reputation.  Given that its virtually impossible to observe the reassignment, this demands some special handling.  Were I confronted with this problem, I'd probably just set up some exponential forgiveness policy or something along these lines.

Shared IP addresses are another issue.  Although this one is often quoted, I have to confess, I've never actually seen this in pratice.  The claim that certain companies, schools, or institutions route all external traffic via the same IP address is entirely plausible.  Granted, I've never specifically sought out a validation of this idea.  Yet, I've analyzed quite a bit of web traffic in my career and never actually observed anything anomolous that could be explained by this line of reasoning.  I suspect any pooling like this is extremely rare in practice.

What's more interesting would be studying the way people move around between IP addresses.  A typical routine for many people includes internet uses at home, work, on a mobile network, occasionally via wifi at prominent places visited (e.g. friend's homes, coffee shops), and atypical one-offs (e.g. hotel rooms).  Having a well manicured database of that type of metadata is something I haven't seen myself.  Sitting on top of that could be some useful models that analyze the movement and usage patterns of legitimate users for the purposes of identifying atypical behavior.  That dream is something I've never been able to justify pursuing, but I suspect we may one day see a 3rd party service specializing in just that task.  While I'll have a lot of questions and skepticism about such a system's accuracy if and when it emerges, I'll also be easy to beta test it!
