import json
import os
import requests
import random
import pprint
import urllib.request
from requests_oauthlib import OAuth1Session


def lambda_handler(event, context):
    
    # Twitterのアクセスキーを設定
    twitter = OAuth1Session(os.environ["CONSUMER_KEY"], os.environ["CONSUMER_SECRET"], os.environ["ACCESS_TOKEN_KEY"], os.environ["ACCESS_TOKEN_SECRET"])
    
    # エンドポイントを設定
    twitter_media_endpoint = "https://upload.twitter.com/1.1/media/upload.json"
    twitter_text_endpoint = "https://api.twitter.com/1.1/statuses/update.json"
    openopus_endpoint = "https://api.openopus.org/work/dump.json"
    youtube_endpoint = "https://www.googleapis.com/youtube/v3/search?type=video&part=snippet&key=" + os.environ["YOUTUBE_API_KEY"] + "&maxResults=1&q="
    
    while True:
        
         # データ初期化
        tweets = ""
        music_datas = requests.get(openopus_endpoint).json()
        composer_data = ""
        work_data = ""
        pop_index_no = []
        works = []
        searchQuery = ""
        
        try:
            # 楽曲データの取得と選択
            while len(works) == 0:
                # 取得した楽曲データの中からランダムに作曲者を取得
                composer_data = music_datas['composers'][random.randrange(len(music_datas['composers']))]
                # 取得した作曲家の作品リスト取得
                works = composer_data['works']
                # 特定の楽曲ジャンルを持つ配列番号を取得する
                for index, work in enumerate(works):
                    if not work['genre'] in  ["Orchestral", "Keyboard", "Chamber"] or not work['popular'] in  ["1"]:
                        pop_index_no.append(index)
                # 取得した配列番号の楽曲を降順に削除する
                for i in sorted(pop_index_no, reverse=True):
                    works.pop(i)
            # 楽曲リストの中からランダムに楽曲を取得
            work_data = works[random.randrange(len(works))]
            # 選択された作曲家と楽曲情報の取得
            composer_name = composer_data['name']
            composer_complete_name =  composer_data['complete_name']
            composer_epoch = composer_data['epoch']
            work_title = work_data['title']
            work_subtitle = work_data['subtitle']
            work_genre = work_data['genre']
            keyword = composer_complete_name + " " + work_title + " " + work_subtitle
            
            searchQuery = keyword.replace(" ", ",")
            
            youtube_data = requests.get(youtube_endpoint + searchQuery).json()
            pprint.pprint(youtube_data)
            videoId = youtube_data['items'][0]['id']['videoId']
            youtube_video_url = "https://www.youtube.com/watch?v=" + videoId
            youtube_sumbnail_url = "https://img.youtube.com/vi/" + videoId + "/mqdefault.jpg"
            
            response = urllib.request.urlopen(youtube_sumbnail_url)
            data = response.read()
            files = {"media" : data}
            req_media = twitter.post(twitter_media_endpoint, files = files)
            
            if req_media.status_code == 200: #成功
                print("Succeed Media Upload !")
            else: #エラー
                print("ERROR : %d"% req.status_code) 
                exit()
            
            # media_id を取得
            media_id = json.loads(req_media.text)['media_id']
            
            tweets += "【今日のクラシック】\n\n"
            tweets += "♬作曲家\n"
            tweets += composer_complete_name + "（" + composer_epoch + "）\n\n" 
            tweets += "♬楽曲\n" 
            tweets += work_title + " " + work_subtitle + "\n"
            tweets += youtube_video_url + "\n\n"
            tweets += "#クラシック音楽\n"
            if work_genre == "Orchestral":
                tweets += "#オーケストラ\n"
            elif work_genre == "Keyboard":
                tweets += "#ピアノ\n"
            elif work_genre == "Chamber":
                tweets += "#室内楽\n"
            tweets += "※動画データの取得は自動で行っています。" 
            
            print(composer_name)
            print(composer_complete_name)
            print(composer_epoch)
            print(work_title)
            print(work_subtitle)
            print(work_genre)
            print(searchQuery)
            
        except:
            print("処理に失敗しました。")
            #break
            
        else:# try中にエラーが検出されなかったときだけツイートを実行する
            
            params = {"status": tweets, "media_ids": media_id} 
            req = twitter.post(twitter_text_endpoint, params = params)
            
            if req.status_code == 200: #成功
                print("Succeed Tweet!")
            else: #エラー
                print("ERROR : %d"% req.status_code) 
            print("=============================================================") 
            print(tweets)
            print("=============================================================")
            break