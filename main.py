import requests, json, argparse, threading

Headers = {'user-agent':'dataparser/1.0'}
FocusStrings = []
BaseUrl = "https://www.reddit.com"


class Scraper(threading.Thread):
    def __init__(self, ParentPost: str, ParentComment = "", CurrentComment = "", CommentBreadth=1, CommentDepth=1):
        threading.Thread.__init__(self)

        self.Children = []
        self.FoundFoci = set()
        self.CurrentComment = CurrentComment
        self.ParentPost = ParentPost
        self.ParentComment = ParentComment
        self.CommentBreadth = CommentBreadth
        self.CommentDepth = CommentDepth

    def search_focus(self, text: str):
        FociSet = set()
        for Focus in FocusStrings:
            # Check if there is a word sperated by whitespaces that is in the FocuStrings list
            if(Focus.lower()[:-1] in text.lower().replace('\n', ' ').split(' ')):
                # Removing last character because it includes newline
                FociSet.add(Focus[:-1])
        
        
        return FociSet

    def spawn_child(self, Comment):
        return Scraper(self.ParentPost, self.CurrentComment, Comment, self.CommentBreadth-1, self.CommentDepth-1)

    def run(self):
        if(self.ParentComment == "" and self.CurrentComment == ""):
            ResponseJSON = requests.get(f'{BaseUrl}{self.ParentPost}.json', headers=Headers).json()

            for i in range(0, self.CommentBreadth):
                # Get a comment to search
                temp = ResponseJSON[1]['data']['children'][i]['data']['permalink']
                # Set the current comment to temp to then set the child's parent comment
                self.CurrentComment = temp
            
                # Make a child
                child = self.spawn_child(self.CurrentComment)
                child.start() # Start it
                self.Children.append(child) # Add it to the children list
            
            for child in self.Children:
                child.join()
        elif(not self.CurrentComment == ""):
            # Format a request and get the json response
            ResponseJSON = requests.get(f'{BaseUrl}{self.CurrentComment}.json', headers=Headers).json()
            temp = ResponseJSON[1]['data']['children'][0]['data']['body']

            FociTemp =self.search_focus(temp)
            self.FoundFoci = FociTemp 
            if(FociTemp != set()):
                print(f'Found {FociTemp}')
            
            # While loop until comments cannot be retrieved
            i=0
            while i < self.CommentBreadth:
                try:
                    temp = ResponseJSON[1]['data']['children'][0]['data']['replies']['data']['children'][i]['permalink']
                    i+=1
                    child = self.spawn_child(temp)
                    child.start()
                    self.Children.append(child)
                except Exception as e:
                    break
            for child in self.Children:
                child.join()
        

def parse():
    parser = argparse.ArgumentParser(description='Recursively search subreddits for mentions of specific stock tickers')
    parser.add_argument('-s', '--subreddit', nargs='+', help='The subreddits you want to search', type=str)
    parser.add_argument('-o', '--output', help='The path you want to output to', type=str)
    parser.add_argument('-p', '--postcount', help='How many posts to search for mentions', default=1, type=int)
    parser.add_argument('-c', '--commentcount', help='How many comments per post to search', default=1, type=int)
    parser.add_argument('-r', '--recursive', help='How deep should it search comment chains', default=1, type=int)
    parser.add_argument('--focustext', help='The path of a file with text you want to search seperated by newlines', default="tickers.csv",type=str)
    

    return parser
def main(Parser: argparse.ArgumentParser):
    Args = Parser.parse_args()
    if(not Args.focustext == None):
        with open(Args.focustext, 'r') as FocusFile:
            global FocusStrings
            FocusStrings = FocusFile.readlines()

    
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
    
    # Args.subreddit: List[str]
    # Iterate through provided subreddits
    JsonOut = dict()
    for Subreddit in Args.subreddit:
        print(f'Starting search in r/{Subreddit}')
        # Normalize input
        Subreddit = Subreddit.split('/')[-1]
        # List of scrape objects
        SubredditScrapers = []
        for i, Post in enumerate(get_posts(Subreddit)):
            if(i >= Args.postcount):
                break
            else:
                # Permalink looks like r/subreddit/comments/gai312/title_of_post
                
                SubredditScrapers.append(Scraper(Post['data']['permalink'], "", "", Args.commentcount))
                SubredditScrapers[i].start()
        # print(f'Formatting data for {Subreddit}')
        for SubScraper in SubredditScrapers:
            SubScraper.join()

            # Check if subreddit is an entry, if not, make a dict for it's entry
            if(not Subreddit in JsonOut):
                JsonOut[Subreddit] = dict()
            # print('Starting recursive read')
            # Make a post entry for each subreddit
            JsonOut[Subreddit][SubScraper.ParentPost] = depth_first_search(SubScraper)
            # print('Finished recursive read')
    print(f'Writing to file {Args.output}')
    with open(Args.output, 'w') as output:
        json.dump(JsonOut, output)
    print('Done')


# Classic depth_first search
def depth_first_search(scraper: Scraper):
    FociDict = dict()
    if(len(scraper.Children) >= 1):
        # For every child
        for Child in scraper.Children:
            # Get the child's FoundFoci set
            for Entry in depth_first_search(Child):
                # If the entry exists add 1 to the count
                # If the entry doesnt exist make an entry and set it to 1
                if(Entry in FociDict):
                    FociDict[Entry] += 1
                else:
                    FociDict[Entry] = 1

        # Return the dict to the original call
        return FociDict
    elif(len(scraper.Children) <= 0):
        return scraper.FoundFoci

                

# Returns a generator of every post returned from subreddit
def get_posts(Subreddit: str):
    ResponseJSON = requests.get(f'{BaseUrl}/r/{Subreddit}.json', headers=Headers).json()
    yield from ResponseJSON['data']['children']    
    


if __name__ == '__main__':
    Parser = parse()
    main(Parser)


