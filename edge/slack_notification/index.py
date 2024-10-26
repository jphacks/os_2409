import os
import slackweb
from dotenv import load_dotenv

load_dotenv()


def __send(msg):
    slack = slackweb.Slack(url=os.getenv("slack_url"))
    slack.notify(text=msg)


def send_poop_complished_msg(used_paper_length, should_user_provide_paper):
    msg = (
        "素晴らしいトイレでした！！\n"
        f"使用したトイレットペーパーの長さ：約{used_paper_length}m\n"
        "トイレ滞在時間：3分20秒\n"
        "ちゃんと手を洗いました！\n\n"
        "そろそろ新しいトイレットペーパーを用意しましょう！"
        if should_user_provide_paper
        else ""
    )
    __send(msg)


if __name__ == "__main__":
    send_poop_complished_msg(0.5, True)
