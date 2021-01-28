import requests, json, argparse

FocusStrings = []
BaseUrl = "https://reddit.com"


class Scraper:
    def __init__(self, ParentPost: str, ParentComment = "", CurrentComment = "",CommentDepth: int):
        self.children = []
        self.CurrentComment = CurrentComment
        self.ParentPost = ParentPost
        self.ParentComment = ParentComment
        self.CommentDepth = CommentDepth
    def spawn_child(self, Comment):
        self.children.append(Scraper(self.ParentPost, self.ParentComment, Comment, self.CommentDepth-1))



def parse():
    parser = argparse.ArgumentParser(description='Recursively search subreddits for mentions of specific stock tickers')
    parser.add_argument('-s', '--subreddit', nargs='+', help='The subreddits you want to search', type=str)
    parser.add_argument('-p', '--postcount', help='How many posts to search for mentions', default=1, type=int)
    parser.add_argument('-c', '--commentcount', help='How many comments per post to search', defualt=1, type=int)
    parser.add_argument('--focusText', help='The path of a file with text you want to search seperated by newlines', default="tickers.csv",type=str)
    

    return parser
def main(Parser: argparse.ArgumentParser):
    Args = Parser.parse_args()
    if(not Args.focusText == None){
        with open(focusText, 'r') as FocusFile:
            FocusStrings = FocusFile.readlines()
    }
    
    # Simple verification that input follows guidelines
    # Try, Excepts to allow for adding beneficial info to the errors
    try:
        assert Args.postcount >= 1
    except AssertionError as e:
        e.args += ('Post count flag needs to be set to 1 or higher')
        raise

    try:
        assert Args.commentcount >= 1
    except AssertionError as e:
        e.args += ('Comment count flag needs to be set to 1 or higher')
        raise
    
    try:
        assert len(Args.subreddit) >= 1
    except AssertionError as e:
        e.args += ('Subreddits not specified')
        raise
    
    Args.subreddit: List[str]
    for Subreddit in Args.subreddit:
        Subreddit = Subreddit.split('/')[-1]
        SubredditScrapers = []
        for i, Post in enumerate(get_posts(f'{BaseUrl}/r/{Subreddit}')):
            if(i > Args.postcount):
                break
            else:
                SubredditScrapers.append(Scraper(Post, "", "", Args.commentcount))
                
                
                

    
def get_posts(Subreddit: str):
    yield post

def get_comments(ParentPost: str, depth: int = 0):
    return
