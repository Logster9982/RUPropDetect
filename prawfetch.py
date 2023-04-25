import praw
import urllib.request
import cv2
import numpy as np
import openai
import re
import time

idr = input("Enter reddit client id: ")
secret = input("Enter reddit client secret: ")
uag = input("Enter reddit useragent: ")
aisec = input("Enter openai API code: ")

#reddit dev data for usage
reddit = praw.Reddit(
    client_id=idr,
    client_secret=secret,
    user_agent=uag,
)

z = int(input("How many hours will the program iterate for? (Put in -1 for no limit): "))
#selects subreddit
sred = input("Enter a subreddit: ")

subreddit = reddit.subreddit(sred)
while z !=0: 
    IsImage = True
    prop = 0

#gets post id for comments
    for submission in subreddit.top(limit=1,time_filter="week"):
        post = (submission.id)
#sets post
    submission = reddit.submission(post)
    rauthor = submission.author

    url = str(submission.url)

    if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"):
        urllib.request.urlretrieve(url, f"test")

    else:
        IsImage = False


    #takes comments to text file
    submission.comments.replace_more(limit=0)
    with open('comments.txt', 'w') as f:
        for top_level_comment in submission.comments:
            f.write(top_level_comment.id + "," + top_level_comment.body + "\n")
        
    count = 0

# Iterate through top submissions
    for submission in subreddit.top(limit=None):

    # Get the link of the submission
        url = str(submission.url)

    # Check if the link is an image
        if url.endswith("jpg") or url.endswith("jpeg") or url.endswith("png"):

        # Retrieve the image and save it in current folder
            urllib.request.urlretrieve(url, f"{sred}{count}")
            count += 1

        # Stop once you have 10 images
            if count == 10:
                break


    count2 = 0
    if IsImage == False:
        count2 = 10

    while count2 < 10:

        try:
        #takes top 10 images from reddit and compares them with test image
            img1 = cv2.imread(sred+str(count2))
            img2 = cv2.imread("test")

            img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

            def mse(img1, img2):
                h, w = img1.shape
                diff = cv2.subtract(img1, img2)
                err = np.sum(diff**2)
                mse = err/(float(h*w))
                return mse, diff

            error, diff = mse(img1, img2)
            error = round(error, 2)
            print(error)

            if error < 3:
                print("Duplicate")
                a = open("disingenuous.txt", "a")
                f.write(rauthor.id, ",", rauthor.name, " post uses repeated content")
                break
            

        except cv2.error as e:
            error = 4

        count2 += 1


# Set up OpenAI API key
    openai.api_key = aisec

# Load the fine-tuned GPT-3 propaganda detection model
    model_engine = "text-davinci-002"
    model_prompt = (f"Davinci-2 is detecting hate speech\n"
                    f"---\n"
                    f"Please classify the following text as hate speech or not hate speech:\n")

# Function to detect propaganda in a given text
    def detect_propaganda(text):
        prompt = model_prompt + text
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.5,
        )
        output_text = response.choices[0].text.strip()
        if re.match(r"propaganda", output_text):
            prop = 1
        else:
            prop = 0

# Read the text file containing the text to be analyzed
    with open("comments.txt") as f:
        text = f.read()

    if prop == 1:
        a = open("disingenuous.txt", "a")
        (rauthor.id, ",", rauthor.name, " post may contain propagana comments")
    time.sleep(3600)
    z -= 1