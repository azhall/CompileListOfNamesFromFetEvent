import csv, re
# import logging
import tkinter as tk

from grab import Grab
import grab.transport
import grab.transport.curl
from tkinter import ttk
from tkinter import messagebox


root = tk.Tk()

username = tk.StringVar()
password = tk.StringVar()
event_url = tk.StringVar()

login_url = 'https://fetlife.com/login'
homepage_url = 'https://fetlife.com/home/v4'

g = Grab()


def get_rsvps_url(): return event_url.get() + '/rsvps/'


def get_maybes_url(): return get_rsvps_url() + '/maybe/'


def get_users_from_page(url):
    """

        :param url:
        :return: a list of usernames
        """
    g.go(url)
    return g.doc.tree.xpath('//div/a[@class="fl-member-card__user"]/text()')


def generate_filename(url):
    """

    :param url:
    """
    g.go(url)
    event_name = g.doc.tree.xpath('//div/h1[@class="h2 bottom"]/text()')[0]

    # Remove non-alphanumeric characters
    regex = re.compile('[^a-zA-Z0-9]')
    event_name = regex.sub('', event_name)

    # Build filename
    # (year-month-day)-(event name)_attendees.csv
    date_segment = g.doc.tree.xpath('//span/span/meta[@itemprop="startDate"]/@content')[0]
    date_segment = date_segment.partition(' ')[0] # Removes zulu-time, included with xpath result
    date_segment = date_segment.replace('-', '_')

    filename = date_segment + "-" + event_name + "_attendees.csv"
    return filename


def go_bind(event):
    go()


def go():
    # logging.basicConfig(level=logging.DEBUG)

    # Go to login page
    g.go(login_url)
    if g.doc.url == login_url: # Verify we still need to log in (IE - didn't get redirected past the login page)
        # Enter name and password
        g.doc.set_input('nickname_or_email', username.get())
        g.doc.set_input('password', password.get())
        g.doc.submit()

        # Confirm login was successful
        if g.doc.url != homepage_url:
            messagebox.showerror('was problem?', "Error trying to login\nWrong username/password?")
            return

    csv_filename = generate_filename(event_url_entry.get())

    with open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

        # First build list from RSVPs, then Maybes
        for u in [get_rsvps_url(), get_maybes_url()]:
            page_url = u
            while True:
                attendee_list = get_users_from_page(page_url)
                for attendee in attendee_list:
                    csv_writer.writerow([attendee])

                # Find url for next page, if it doesn't exist break out of infinite loop
                next_page_part = g.doc.tree.xpath('//div/a[@class="next_page"]/@href')
                # If there's no next page link, we're outtie 5,000
                if not next_page_part:
                    break
                page_url = 'https://fetlife.com' + next_page_part[0]


####################
# Starts here
####################
root.title("Get list of attendees")
root.resizable(0, 0)

main_frame = ttk.Frame(root, padding="3 3 12 12")
main_frame.grid(column=2, row=1, sticky=(tk.W, tk.E))
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(0, weight=1)

ttk.Label(main_frame, text="Username").grid(row=1, sticky=tk.W)
username_entry = ttk.Entry(main_frame, textvariable=username)
username_entry.grid(row=2, sticky=(tk.W, tk.E))

ttk.Label(main_frame, text="Password").grid(row=3, sticky=tk.W)
password_entry = ttk.Entry(main_frame, width=36, textvariable=password, show="*")
password_entry.grid(row=4, sticky=(tk.W, tk.E))

ttk.Label(main_frame, text="Event URL (Ex: https://fetlife.com/events/434286/").grid(row=5, sticky=tk.W)
event_url_entry = ttk.Entry(main_frame, width=36, textvariable=event_url)
event_url_entry.grid(row=6, sticky=(tk.W, tk.E))

go_button = ttk.Button(main_frame, text="Go get 'em", command=go)
go_button.grid(row=7, sticky=tk.E)

for child in main_frame.winfo_children(): child.grid_configure(padx=5, pady=5)

username_entry.focus()
root.bind('<Return>', go_bind)


##############################
# For debugging
##############################
# username_entry.insert(0, "")
# password_entry.insert(0, "")
event_url_entry.insert(0, "https://fetlife.com/events/")


root.mainloop()