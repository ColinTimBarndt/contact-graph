# Contact Graph

I want to analyze my social connections on various platforms and visualize them. When meeting new people around Germany
I noticed that many people knew other friends of mine even though they were living on the opposite sides of the
country. By this private project I want to get some insight.

## How to run

At the moment, data generation and analysis are split for performance reasons. Data loaders need to be configured when
there exists a template file for them. Just remove the `.template` from the file name and fill in the config.

To export your Telegram data, run the according shell script. It is going to log into your account as a client and save
your chat and group relations to a pickle file.

To display a graph of the generated `telegram.pickle`, run `python3 visualize.py`.