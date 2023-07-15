from django.shortcuts import render, redirect
from django.http import JsonResponse
import tweepy
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import pandas as pd
from django.http import FileResponse
import os


API_KEY = "**************************"
API_SECRET = "*****************************"
# ACCESS_TOKEN = "1258339053478567936-pMckZ4JVdTlA8TqReLojEOHrjo7mn0"
# ACCESS_TOKEN_SECRET = "VFvSDQHiayLmRlgOiMaEspXc8fnzVboCGOXUPQOGQoIFM"
CALLBACK_URL = "http://127.0.0.1:8000/callback"
AUTH = tweepy.OAuthHandler(API_KEY, API_SECRET, callback=CALLBACK_URL)

def sync(id):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    r = api.verify_credentials()
    followers=api.get_followers()
    followerslist=[]
    for follower in followers:
        followerslist.append(follower.screen_name)

    recentFollowers={}
    for follower in followers:
        recentFollowers.update({
            follower.id : {
                "profile_image_url":follower.profile_image_url,
                "name":follower.name,
                "screen_name":follower.screen_name,
                "followers_count":follower.followers_count,
                "following": follower.friends_count,
                "follow_back": 100 if round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1)>=100 else round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1),
                "created_at": str(follower.created_at)[0:11]
                }
            })

    friendship= api.get_friends()
    friendslist=[]
    for i in friendship:
        friendslist.append(i.screen_name)


    Non_followers = r.friends_count - r.followers_count
    user_data = {
        "name": r.name,
        "username": r.screen_name,
        "profile_image": r.profile_image_url,
        "account_age": r.created_at,
        "followers_count": r.followers_count,
        "following_count": r.friends_count,
        "non_followers": Non_followers,
        "follow_back": 100 if round((r.friends_count/(1 if r.followers_count==0 else r.followers_count))*100, 1)>=100 else round((r.friends_count/(1 if r.followers_count==0 else r.followers_count))*100, 1),
        "followers": recentFollowers,
        "followings": friendslist,
    }


def index(request):
    return render(request, "index.html")


def login(request):
    auth_url = AUTH.get_authorization_url()
    request.session['request_token'] = AUTH.request_token
    return redirect(auth_url)


def callback(request):
    verifier = request.GET.get('oauth_verifier')
    request_token = request.session.pop('request_token', None)
    # if not verifier or not request_token:
    #     pass
    AUTH.request_token = request_token
    AUTH.get_access_token(verifier)
    access_token = AUTH.access_token
    access_token_secret = AUTH.access_token_secret
    request.session['access_token'] = access_token
    request.session['access_token_secret'] = access_token_secret
    return redirect('/dashboard')


def dashboard(request):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    r = api.verify_credentials()
    followers=api.get_followers()
    followerslist=[]
    for follower in followers:
        followerslist.append(follower.screen_name)

    recentFollowers={}
    for follower in followers:
        recentFollowers.update({
            follower.id : {
                "profile_image_url":follower.profile_image_url,
                "name":follower.name,
                "screen_name":follower.screen_name,
                "followers_count":follower.followers_count,
                "following": follower.friends_count,
                "follow_back": 100 if round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1)>=100 else round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1),
                "created_at": str(follower.created_at)[0:11]
                }
            })

    friendship= api.get_friends()
    friendslist=[]
    for i in friendship:
        friendslist.append(i.screen_name)
    # print(r.followers_count)

    Non_followers = r.friends_count - r.followers_count
    data = {
        "FollowerCount": r.followers_count,
        "FollowingCount": r.friends_count,
        "NonFollowers": Non_followers,
        "follow_back": 100 if round((r.friends_count/(1 if r.followers_count==0 else r.followers_count))*100, 1)>=100 else round((r.friends_count/(1 if r.followers_count==0 else r.followers_count))*100, 1),
        "RecentFollowers": recentFollowers
    }
    image=r.profile_image_url
    return render(request, 'dashboard/dashboard.html', data)


def follow(request):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    r = api.verify_credentials()
    friendship= api.get_friends()
    friendslist={}
    for follower in friendship:
        friendslist.update({
            follower.id : {
                "profile_image_url":follower.profile_image_url,
                "name":follower.name,
                "screen_name":follower.screen_name,
                "followers_count":follower.followers_count,
                "following": follower.friends_count,
                "following_back": follower.following,
                "follow_back": 100 if round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1)>=100 else round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1),
                "created_at": str(follower.created_at)[0:11]
                }
            })
        
    return render(request, 'dashboard/follow.html', {"followers" : friendslist})

def nonfollowers(request):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    r = api.verify_credentials()
    followers=api.get_followers()
    followerslist=[]
    for follower in followers:
        followerslist.append(follower.id)
    friendship= api.get_friends()
    friendslist={}
    for i in friendship:
        friendslist.update({
            i.id : [i.profile_image_url, i.name, i.screen_name]
        })
    Non_followers = {}
    for item in friendslist:
        if item not in followerslist:
            Non_followers.update({
                item : {
                    "profile_image_url":friendslist[item][0],
                    "name":friendslist[item][1],
                    "screen_name":friendslist[item][2]
                    }
                })
    # Non_followers = [item for item in friendslist if item not in followerslist]
    # print(Non_followers)
    return render(request, 'dashboard/non_followers.html', {"Non_followers" : Non_followers})

def followers(request):
    api = tweepy.API(AUTH)
    followers=api.get_followers()
    followerslist={}
    for follower in followers:
        followerslist.update({
            follower.id : {
                "profile_image_url":follower.profile_image_url,
                "name":follower.name,
                "screen_name":follower.screen_name,
                "followers_count":follower.followers_count,
                "following": follower.friends_count,
                "following_back": follower.following,
                "follow_back": 100 if round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1)>=100 else round((follower.friends_count/(1 if follower.followers_count==0 else follower.followers_count))*100, 1),
                "created_at": str(follower.created_at)[0:11]
                },
            })

    return render(request, 'dashboard/followers.html', {"data" : followerslist})


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def follow_user(request):
    api = tweepy.API(AUTH)
    if request.method == "POST":
        screen_name = request.POST.get('screen_name')
        # print(screen_name)
        try:
            api.create_friendship(screen_name=screen_name)
        except Exception as e:
            return JsonResponse({"error" : e}, status=400)        
        return JsonResponse({"success" : "Follow successfull"}, status=200)
    else:
        return JsonResponse({"error" : "Request failed"}, status=400)


def unfollow_user(request):
    api = tweepy.API(AUTH)
    if request.method == "POST":
        screen_name = request.POST.get('screen_name')
        # print(screen_name)
        try:
            api.destroy_friendship(screen_name=screen_name)
        except Exception as e:
            return JsonResponse({"error" : e}, status=400)        
        return JsonResponse({"success" : "Unfollow successfull"}, status=200)
    else:
        return JsonResponse({"error" : "Request failed"}, status=400)


def search_users(request, search_query):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    r = api.verify_credentials()
    data = {
        "Users": r.search_users(q=search_query),
    }
    return JsonResponse({"data": data}, status=200)

def analysis(request):
    return render(request, 'dashboard/analysis.html')



def sentiments(request):
    if request.method == 'POST':
        data = request.POST.get('input_data')
        # print(data)
    # Process the data or perform any required operations
    consumer_key = "****************************"
    consumer_secret = "********************************"
    access_token = "****************************************"
    access_token_secret = "************************************88"

    # Authentication with Twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    # update these for the tweet you want to process replies to 'name' = the account username and you can find the tweet id within the tweet URL
    val = data


    a=val.split("/")
    screenname=a[-3]
    tweet_id =a[-1]

    # print(screenname)
    # print(tweet_id)
    replies=[]

    for tweet in tweepy.Cursor(api.search_tweets,q='to:'+screenname, result_type='recent').items(100):
        if hasattr(tweet, 'in_reply_to_status_id_str'):
            if (tweet.in_reply_to_status_id_str==tweet_id):
                replies.append(tweet)

    tweetlist=[]
    for tweet in replies:
            row = tweet.text.replace('\n', ' ')
            tweetlist.append(row)

    # print(tweetlist)
    # print(len(tweetlist))
            
    neg=0
    neut=0
    pos=0

    for i in tweetlist:
        tweet=i


        # # tweet = "@MehranShakarami today's cold @ home 😒 https://mehranshakarami.com"
        # tweet = 'Hamza bhi miss u so much, we know everything... What good days those were💔'

        # precprcess tweet
        tweet_words = []

        for word in tweet.split(' '):
            if word.startswith('@') and len(word) > 1:
                word = '@user'
            
            elif word.startswith('http'):
                word = "http"
            tweet_words.append(word)

        tweet_proc = " ".join(tweet_words)

        # load model and tokenizer
        roberta = "cardiffnlp/twitter-roberta-base-sentiment"

        model = AutoModelForSequenceClassification.from_pretrained(roberta)
        tokenizer = AutoTokenizer.from_pretrained(roberta)

        labels = ['Negative', 'Neutral', 'Positive']

        # sentiment analysis
        encoded_tweet = tokenizer(tweet_proc, return_tensors='pt')
        # output = model(encoded_tweet['input_ids'], encoded_tweet['attention_mask'])
        output = model(**encoded_tweet)

        scores = output[0][0].detach().numpy()
        scores = softmax(scores)
        
        neg+=scores[0]
        neut+=scores[1]
        pos+=scores[2]
        

    negative=neg/len(tweetlist)
    neutral=neut/len(tweetlist)
    postive=pos/len(tweetlist)


    negative=negative*100
    postive=postive*100
    neutral=neutral*100

    print("Negative",negative)
    print('Neutral',neutral)
    print("positive",postive)

    # i am stopping here because of that the url i put in
    return render( request,'dashboard/sentiments.html', {'negative': negative,'postive': postive,'neutral' : neutral, 'tweetlist': tweetlist})

def  blockeduser(request):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    blocked_users = api.get_blocks()
    blocks=[]
    blocks1=[]
    # Iterate over the blocked users and print their screen names
    for user in blocked_users:
        blocks1.append(user.screen_name)
        blocks1.append(user.followers_count)

        blocks1.append(user.friends_count)
        # print(user)
        blocks.append(blocks1)
        blocks1=[]
    # print(blocks)
    return render( request, 'dashboard/blockedusers.html',{'blocks':blocks})



def tweet(request):
    api = tweepy.API(AUTH, wait_on_rate_limit=True)
    
    if request.method == 'POST':
        field_value = request.POST.get('field_name')
        # print(field_value)
        okay= str(field_value)
        api.update_status(field_value)
        

    


    return render(request,'dashboard/tweet.html')



dataframe1 = pd.read_excel('dev/data.xlsx')
column_data = dataframe1["Column_Name"]


Followers = column_data.tolist()




def suggest(request):
    followerslist={}

    for follower in Followers:
        followerslist.update({
            follower: {
                "screen_name": follower
            }
        })
  
    


    return render(request,"dashboard/FollowersSuggestion.html",{'data':followerslist})






