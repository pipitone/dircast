from feedgen.feed import FeedGenerator

def format_itunes_duration(td):
    return "{hours:02d}:{minutes:02d}:{seconds:02d}".format(
        hours=td.seconds//3600,
        minutes=(td.seconds//60)%60,
        seconds=int(td.seconds%60)
    )

def add_entry(fg, md):
    fe = fg.add_entry()
    fe.id(md.id)
    fe.title(md.title)
    fe.enclosure(md.link, str(md.length), "audio/mpeg")
    fe.published(md.date)
    if md.duration is not None:
        fe.podcast.itunes_duration(format_itunes_duration(md.duration))
    if md.description is not None:
        fe.description(md.description)

def generate_feed(channel_dict, file_metadatas):
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.link(href=channel_dict["url"], rel="self")
    fg.title(channel_dict["title"])
    fg.description(channel_dict["description"])
    fg.author(channel_dict.get("author", None))
    
    fg.podcast.itunes_image(channel_dict.get('image_url', None))
    fg.podcast.itunes_category(channel_dict.get('category', None))

    for file_metadata in file_metadatas:
        add_entry(fg, file_metadata)

    return fg.rss_str(pretty=True)
