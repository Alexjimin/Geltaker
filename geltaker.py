import aiohttp
from pygelbooru import Gelbooru 
import asyncio
import os

api_key, user_id = ("4d54cfbad09bf4c0982614c4a1dea4338bdc8e1734201a524b728b8704d5d9fd", "862077")
gelbooru = Gelbooru(api_key, user_id)

def show_menu(selections: list[str]):
    """
    Prints a menu of options to the user.

    selections: A list of strings to be printed as options.
    """
    list(print(f"{i+1}. {selection}") for i, selection in enumerate(selections))

def get_user_input():
    """
    Gets user input from the command line.

    Returns: The user's input as a string.
    """
    return input("> ")

def prompt_add_tags():
    """
    Prompts the user to add tags to the search.
    Returns a list of tags.
    """
    print("\nEnter tags to add, seperated by commas: ")
    print("Example: kakure eria, rating:explicit")
    user_input_tag = get_user_input().split(",")
    user_input_tag = [tag.strip() for tag in user_input_tag]
    user_input_tag = [tag.replace(" ", "_") for tag in user_input_tag]
    return user_input_tag

def prompt_remove_tags(tags):
    """
    Prompts the user to remove tags from the search.
    Returns modified list of tags. Does not modify original list, do not append.
    Returns None if no tags to remove.
    """
    print("\nEnter the index of the tag to remove (0 to go back): ")
    print("0. go back")
    for i, tag in enumerate(tags):
        print(f"{i+1}. {tag}")
    while True:
        selection = get_user_input()
        if selection == "0":
            return
        try:
            selection = int(selection)
            if selection > 0 and selection <= len(tags):
                return tags[selection-1]
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid selection.")

def check_directory_exists(path: str, create: bool = False):
    """
    Checks if a directory exists.
    Can crete the directory.
    path: path to directory to check.
    create: create the directory if it does not exist.
    """
    if not os.path.exists(path):
        if create:
            os.mkdir(path)

async def download_post(post, path: str):
    """
    Downloads a post from a url.
    post: post to download.
    path: path to download the post to.
    """
    # download the post
    async with aiohttp.ClientSession() as session:
        # get the extension of the file from the url
        print(f"Downloading {post.file_url}")
        extension = post.file_url.split(".")[-1]
        async with session.get(str(post)) as response:
            # save the post
            with open(f"{path}/{int(post)}.{extension}", "wb") as file:
                file.write(await response.read())

async def gelbooru_search(tags: list[str], limit: int = 20):
    results = await gelbooru.search_posts(tags=tags, limit=limit)
    # download the posts asynchronously
    tasks = [download_post(post, "./arts") for post in results]
    await asyncio.gather(*tasks)

def prompt_search_and_download(tags: list[str], limit: int = 20, path: str = "./arts"):
    """
    Searches gelbooru for posts with the given tags and downloads them to specified directory.
    tags: list of tags to search for.
    limit: number of posts limiting the number of downloads.
    path: directory to download the posts to.
    """
    check_directory_exists(path, create=True)
    # run search and save results
    asyncio.run(gelbooru_search(tags, limit))

def prompt_settings(posts_limit, arts_path):
    options = ["Change posts limit", "Change arts path"]
    while True:
        print("\nSettings:")
        print(f"Posts limit: {posts_limit}")
        print(f"Arts path: {arts_path}")
        print("0. go back")
        show_menu(options)
        selection = get_user_input()
        if selection == "0":
            break
        elif selection == "1":
            print("Enter the new posts limit: ")
            posts_limit = get_user_input()
        elif selection == "2":
            print("Enter the new arts path: ")
            arts_path = get_user_input()
    return posts_limit, arts_path

def prompt_main_menu():
    tags = []
    posts_limit = 20
    arts_path = "./arts"
    options = ["Add tags", "Remove tags", "Search", "Settings", "Exit"]
    while True:
        print("\n")
        print("Current tags: ", end="")
        if not tags:
            print("(No tags)", end="")
        for tag in tags:
            # remove trailing comma. i know this is ugly but i like this way 
            print(tag, end=", " if tag is not tags[-1] else "") 
        print()
        show_menu(options)
        selection = get_user_input()
        if selection == "1":
            list(tags.append(tag) for tag in prompt_add_tags())
        elif selection == "2":
            tag_to_remove = prompt_remove_tags(tags)
            if tag_to_remove is not None:
                tags.remove(tag_to_remove)
        elif selection == "3":
            prompt_search_and_download(tags, int(posts_limit), arts_path)
        elif selection == "4":
            posts_limit, arts_path = prompt_settings(posts_limit, arts_path) # huh ugly code uwu
        elif selection == "5":
            print("goodbye")
            # end asyncio loop
            return

if __name__ == "__main__":
    prompt_main_menu()
