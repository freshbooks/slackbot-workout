import random
import time
import requests
import json
import csv
import os

USERTOKENSTRING =  os.environ.get('SLACK_USER_TOKEN')
URLTOKENSTRING =  os.environ.get('SLACK_URL_TOKEN')
TEAMNAMESTRING = os.environ.get('SLACK_TEAM_NAME')
CHANNEL = os.environ.get('SLACK_CHANNEL')

# Extracts online users from Slack API
def extractSlackUsers(token):
    # Set token parameter of Slack API call
    tokenString = token
    params = {
        "token": tokenString,
    }

    response = requests.get("https://slack.com/api/channels.list", params=params)
    channels = json.loads(response.text, encoding='utf-8')['channels']
    for channel in channels:
        if channel['name'] == CHANNEL:
            params['channel'] = channel['id']
            break

    # Capture Response as JSON
    response = requests.get("https://slack.com/api/channels.info", params=params)
    channel = json.loads(response.text, encoding='utf-8')["channel"]
    user_ids = channel["members"]
    users = []
    for user in user_ids:
        params = {
            "token": tokenString,
            "user": user
        }

        response = requests.get("https://slack.com/api/users.info", params=params)
        users.append(json.loads(response.text, encoding='utf-8')["user"])

    def findUserNames(x):
        if getStats(x) is False:
            return None
        name = "@" + x["name"].encode('utf-8')
        return name.encode('utf-8')

    def getStats(x):
        params = {"token": tokenString, "user": x["id"]}
        response = requests.get("https://slack.com/api/users.getPresence", params=params)
        status = json.loads(response.text, encoding='utf-8')["presence"]
        return status == "active"

    return filter(None, list(map(findUserNames, users)))


# Selects Next Time Interval and Returns the Exercise
def selectExerciseAndStartTime():

    # Exercise (2 Forms of Strings)
    exercises = [" PUSHUPS ", " SECOND PLANK ", " SITUPS ", " SECOND WALL SIT ", " SQUATS ", " LUNGES ", " TUCK JUMPS ", " DIPS ", " JUMPING JACKS "]
    exerciseAnnouncements = ["PUSHUPS", "PLANK", "SITUPS", "WALLSIT", "SQUATS", "LUNGES", "TUCK JUMPS", "DIPS", "JUMPING JACKS"]

    # Random Number generator for Reps/Seconds and Exercise
    nextTimeInterval = random.randrange(300, 1800)
    exerciseIndex = random.randrange(0, 9)

    # Announcement String of next lottery time
    lotteryTimeString = "NEXT LOTTERY FOR " + str(exerciseAnnouncements[exerciseIndex]) + " IS IN " + str(nextTimeInterval/60) + " MINUTES"

    requests.post("https://"+ TEAMNAMESTRING +".slack.com/services/hooks/slackbot?token="+URLTOKENSTRING+"&channel=%23"+CHANNEL, data=lotteryTimeString)

    # Sleep until next lottery announcement
    time.sleep(nextTimeInterval)

    # Return exercise
    return str(exercises[exerciseIndex])


# Selects the exercise lottery winner
def selectPerson(exercise):

    # Select number of reps
    exerciseReps = random.randrange(10, 30)

    # Pull all users from API
    slackUsers = extractSlackUsers(USERTOKENSTRING)
    slackUsers.append('@group')

    # Select index of team member from array of team members
    selection = random.randrange(0, len(slackUsers))
    if slackUsers[selection] != '@group':
        slackUsers.remove('@group')
        slackUsers.remove(slackUsers[selection])

        lotteryWinnerString = str(exerciseReps) + str(exercise) + "RIGHT NOW " + slackUsers[selection]
        if len(slackUsers) > 18:
            selection2 = random.randrange(0, len(slackUsers))
            lotteryWinnerString += " AND " + slackUsers[selection2]

        requests.post("https://"+ TEAMNAMESTRING +".slack.com/services/hooks/slackbot?token="+URLTOKENSTRING+"&channel=%23"+CHANNEL, data=lotteryWinnerString)
    else:
        lotteryWinnerString = str(exerciseReps) + str(exercise) + "RIGHT NOW " + slackUsers[selection]
        requests.post("https://"+ TEAMNAMESTRING +".slack.com/services/hooks/slackbot?token="+URLTOKENSTRING+"&channel=%23"+CHANNEL, data=lotteryWinnerString)

for i in range(10000):
    exercise = selectExerciseAndStartTime()
    selectPerson(exercise)
