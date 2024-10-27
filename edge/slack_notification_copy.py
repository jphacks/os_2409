import os
import slackweb
# import sys

# sys.path.append("../")d
from save2firestore.index import get_unch_type


def __send(msg):
    slack = slackweb.Slack(url=os.getenv("https://hooks.slack.com/services/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"))
    slack.notify(text=msg)


def send_poop_complished_msg(used_paper_length, should_user_provide_paper):
    msg = (
        "<<トイレリザルト>>\n"
        f"出したうんちの種類：{get_unch_type().get_name()}\n"
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