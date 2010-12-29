import urllib
import urllib2
import os.path
import sys
from BeautifulSoup import BeautifulSoup

class Piccsy():
    _piccsyURL="http://piccsy.com"
    _pageURL="http://piccsy.com/user/piccs?kohana_uri=user%2Fpiccs%2F&page="
    
    def __init__(self,username,password):
    # Check if username and password are empty
    # If not, set attributes and login to piccsy.
        if username and password:
            self.username=username
            self.password=password
            self.login()
        else:
    # *** Do something if username and password are empty ***
    # Although it will be caught at login, saves resources.
            pass
            
    def login(self):
        """Attempts to login to piccsy with supplied credentials."""

        login_title="Piccsy :: Image Bookmarking :: Login"
        # Build and install cookie opener
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(opener)

        # URLEncode username and password
        params=urllib.urlencode(dict(username=self.username,
                                     password=self.password))
            
        # Try to login and catch when login fails.
        login_page=opener.open(self._piccsyURL+'/auth/login/',params)
        soup=BeautifulSoup(login_page)
        login_page.close()

        if soup.head.title.text==login_title:
            sys.stderr.write('Could not log in, check username and password.')
            sys.exit(2)

        
        
    def get_last_page(self):
        """ Determines total number of user picc pages."""
        # Try to open the first user page, exit if something goes wrong.
        try:
            page=urllib2.urlopen(self._piccsyURL+"/user/piccs")
        except urllib2.URLError,err:
         # *** Need to handle this error better. ***
            sys.stderr.write('ERROR: %s\n' % str(err))
            return -1
        
        # Determine the last user page
        # The number is stored in a div with id "pager"; it is in
        # the second-to-last link.
        soup=BeautifulSoup(page)
        pager=soup.find('div',id="pager")
        pager_links=pager.findAll('a')
        
        if pager_links[-2]:
            try:
                lastpage=int(pager_links[-2].text)
            except ValueError,err:
                sys.stderr.write('ERROR: %s\n' % str(err))
                return -1
            
        return lastpage

    

    def save_image(self,img_post,dl_dir,overwrite):
        """ Saves an image given its individual post page."""
        # Attempt to open the individual post page
        try:
            img_page=urllib2.urlopen(img_post)
        except urllib2.URLError,err:
            #### Write proper error handling here. ####
            sys.stderr.write('ERROR: %s\n' % str(err))
            return -1
        
        # Soup the image page
        img_page_soup=BeautifulSoup(img_page)

        # Get the actual image URL and file name.
        img_link=img_page_soup.find('div',id="indivPost-leftColumn").img['src']
        img_file_name=img_link.split("/")[-1]
        
        # Create the local file name.
        local_name=os.path.join(dl_dir,img_file_name)

        # If overwrite is False, need to check if local name already exists.
        if not overwrite and os.path.exists(local_name):
            #### Do proper error handling here. ####
            sys.stderr.write('ERROR: File already exists.')
            return -1

        # Open up image and write to disk.
        try:
            img=urllib2.urlopen(img_link)
        except urllib2.URLError,err:
            #### Write proper error handling here. ####
            sys.stderr.write('ERROR: %s\n' % str(err))
            return -1
        else:
            try:
                with open(local_name,"wb") as output:
                    output.write(img.read())
            except IOError,err:
                #### Proper Error Handling Here. ####
                sys.stderr.write('ERROR: %s\n' % str(err))
                return -1
            
            
    def download_images(self,dl_dir="",start=1,end=-1,overwrite=False):
        """ Download picc'd images into dl_dir from pages start to end.
        If start and end are not specified, downloads all picc'd images.
        If dl_dir is not specified, uses current directory.
        Set overwrite to true if you want to overwrite existing files
        if necessary in dl_dir."""

        # Check if dl_dir is a valid directory path.
        if not os.path.isdir(dl_dir):
            sys.stderr.write('ERROR: Invalid directory path.')
            return -1

        # Check to see that start<=end
        if start>end:
            sys.stderr.write('ERROR: Start must be leq to end.')
            return -1
        
        # If end=-1, we are downloading all picc'd images, so get last page num
        if end==-1:
            end=self.get_last_page()
            #### Handle Error case here ####

        # Open every user page in range
        for pg_num in range(start,end+1):
            # Try to open the image index page.
            try:
                index_page=urllib2.urlopen(self._pageURL+str(pg_num))
            except urllib2.URLError,e:
                sys.stderr.write('ERROR: Trying to open %s,  %s\n' % (pageurl+
                                                      str(pg_index),str(err)))
                return -1

            # Soup the page.
            index_soup=BeautifulSoup(index_page)

            # Find all the image divs
            img_divs=index_soup.findAll('div',{"class":"image"})

            # Get all absolute links for image posts.
            #### This seems a bit risky, but it works for now. ####
            img_posts=[self._piccsyURL+img.find('a')['href']
                       for img in img_divs]

            # Download every image from its individual post page.
            for post in img_posts: self.save_image(post,dl_dir,overwrite)
            
                
                
            

        

        

        

        
                
        
        
    
