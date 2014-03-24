import os
from scrubber import Scrubber
import BeautifulSoup
#import BeautifulSoup

# initialise the scrubber! all this stuff is overriding scrubber defaults so hack it to bits if you want!
scrubber = Scrubber(autolink=False)
scrubber.allowed_tags = set((
    'a', 'abbr', 'acronym', 'b', 'bdo', 'big', 'blockquote', 'br',
    'center', 'cite', 'code',
    'dd', 'del', 'dfn', 'div', 'dl', 'dt', 'em',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins',
    'kbd', 'li', 'ol', 'param', 'pre', 'p', 'q',
    's', 'samp', 'small', 'span', 'strike', 'strong', 'sub', 'sup',
    'table', 'tbody', 'td', 'th', 'thead', 'tr', 'tt', 'ul', 'u',
    'var', 'wbr',
))
scrubber.disallowed_tags_save_content = set((
    'blink', 'body', 'html','font',
))
scrubber.allowed_attributes = set((
    'align', 'alt', 'border', 'cite', 'dir',
    'height', 'href', 'src', 'title', 'type', 'width',
    'face', 'size', # font tags
    'flashvars', # Not sure about flashvars - if any harm can come from it
    'classid', # FF needs the classid on object tags for flash
    'name', 'value', 'quality', 'data', 'scale', # for flash embed param tags, could limit to just param if this is harmful
    'salign', 'align', 'wmode',
)) # Bad attributes: 'allowscriptaccess', 'xmlns', 'target'
scrubber.normalized_tag_replacements = {'b': 'strong', 'i': 'em'}
# any giveaway classes the definately identify a footer.
footer_classes = ['gmail_quote', 'moz-signature']
# used for "on the 25th of DEC so and so wrote:" style patterns
dates = ['JAN', 'FEB' , 'MAR', 'APR' , 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
# Giveaway email reply strings
email_heads = ['FROM', 'TO', 'SUBJECT']
# we can boost certainty of a signoffNodes significantly by looking for common one-liners like "cheers" <- a word many people say online but not IRL?
common_signoffs = ['thanks', 'cheers', 'thankyou' 'thank you', 'regards', 'sincerely']
# When we are trying to detect a line, we need to know if an element is inline. these are the ones we are likely to encounter in an email (no textarea) (:
inline_elements = ['A','ABBR','ACRONYM','B','BIG','CITE','CODE','EM','FONT','I','IMG','SMALL','SPAN','STRIKE','STRONG','SUB','SUP','U',]

def split_html_message(messageText, tolerance = {
                                      'comment'        : 3,
                                      'seek'           : 10,
                                      'words_per_line' : 3,
                                      'paranoia'       : 4,
                                    }):
  """
  Html footer splitter, complimentary to text version:
  https://source.iopen.net/groupserver/gs.group.messages.post/files/tip/gs/group/messages/post/postbody.py#L165
    ARGUMENTS
      "messageText" str : The (somewhat) sanitised text to process.
      "tolerance" dict or int : {'comment' : 5, 'seek' : 10m, words_per_line : 3, paranoia : 5 }
        comment        - How lenient to be with ">" reply section and newlines before snipping.
        seek           - Sometimes we need to seek ahead or back around an element to make sure. How many next / previous steps shall we take? remember next != nextSibling
        words_per_line - when we are guessing based on text patterns looking for short lines, how many words per line shal we consider suspicious?
        paranoia       - when we need to make a guess about wheter to keep or to snip. such as when looking for organic signoffNodess by line length, how many hints need to match before we are convinced.
  """

  if isinstance(tolerance, int):
    tolerance = {
      'comment'        : tolerance,
      'seek'           : tolerance * 2,
      'words_per_line' : int(tolerance / 2),
      'paranoia'       : tolerance
    }

  #Will hold the footer string. The main text is whatever is left over :)
  footerNodes = []
  footerText = ""
  #keep track of a confirmed footer
  footer_found = False

  # Create an object that represents the html tree. Erroneously refer to it as a DOM
  # p.s you would not beleive what a BASTARD trailing whitespace can be... actually you probably would.
  dom = strip_empty_tags(BeautifulSoup.BeautifulSoup(messageText.strip()))

  element = dom.contents[0]
  # Now we basically loop / walk our way through the tree.
  # element next gives us the child of element OR the element's nearest neighbour.
  while element:

    #scrubber doesn't reliably strip doctype declarations, but we sure as hell don't want them
    if isinstance(element, BeautifulSoup.Declaration):
        declaration_type = str(element).split()[0]
        if declaration_type.upper() == 'DOCTYPE':
          next = element.next
          element.extract()
          element = next



    # returns true if something footer-like is found AND it's not at the top
    # skip if we have already located the start of the footer
    if not footer_found and is_footer(element, tolerance):
      if is_first(element):
        element = element.nextSibling
        continue
      else:
        footer_found = True
        #print 'footer found -- '  + str(element)

    #now we know enough about what's nearby, whip this guy out of the dom
    if footer_found:
      footerNodes.append(element)
      #in case there are no siblings
      if element.nextSibling:
        element = element.nextSibling
      elif element.parent.nextSibling:
        element = element.parent.nextSibling
      else:
        element = element.next
    else:
      element = element.next


  #Stringify the footer nodes and pull them out of the tree
  for node in footerNodes:
    footerText += str(node)
    node.extract()

  #let's remove any trailing empty tags.
  dom = strip_trailing_rubbish(dom)
  # ok quick sanity check
  # make sure we didn't accidentally nuke the whole document
  if len(dom.text.strip()) < 1:
    dom = strip_empty_tags(BeautifulSoup.BeautifulSoup(messageText.strip()))

  # Now then. if there was some dumb client footer AFTER the reply text,
  # it will have been nuked when the footer was identified
  # but some people /clients put stuff above the bottomquote / footer
  # This is fiendishly hard to identify as it containts things like

  # we'll start at the top again and rock down the tree looking for short lines and doing other sniffing
  # see : is_signoff()

  element = dom.contents[0]
  while element:
    top = is_signoff(element, tolerance)
    if top:
      break
    else:
      element = element.next

  signoffNodes = [] #as with the footer, we'll append nodes here then render them out
  signoffText = '' #as with the footer, we'll render the nodes into text and store them here then PREpend them to the footer string.
  while top:
    signoffNodes.append(top)
    #in case there are no siblings
    if top.nextSibling:
      top = top.nextSibling
    elif top.parent.nextSibling:
      top = top.parent.nextSibling
    else:
      top = top.next


  if len(signoffNodes) > 0:
    for node in signoffNodes:
      signoffText += str(node)
      node.extract()


  dom = strip_trailing_rubbish(dom)
  # just for readability lets poke these into vars before returning them

  # because we are paranoid, another sanity check
  # if len(dom.text.strip()) < 1:
  mainText = scrubber.scrub(dom.prettify())
  footerText = scrubber.scrub(signoffText) + scrubber.scrub(footerText)
  # else:
  #   # if there was a major ballsup just return the whole thing... and throw away about a billion cpu cycles
  #   mainText = scrubber.scrub(messageText)
  #   footerText = ''

  return (mainText.encode('utf8'), footerText.encode('utf8'))

def is_first(node):
  '''
  As with the last node, knowing that our element is _NOT_ the first significant element
  in the tree helps us be more certain that we have a true matches.
  Some messages start with quotes to give the message context, these run the risk of being
  identified as bottom quotes.

  returns True if there is nothing above the BeautifulSoup node except opening markup,

  WARNING: because we are recursively walking down the tree and this method is walking back up it,
  if you just chuck it in a node.next loop it'll correctly identify an element as first, the loop will then drop
  into it and the whole goose will be cooked!
  '''

  if not node.previousSibling:
    if not node.previous:
      return True

    while node:
      # Walk backwards up, if you find anything that isnt an empty / opening tag abort.
      if isinstance(node.previous, BeautifulSoup.Tag):
        if node.previous.name == 'body':
          return True
        node = node.previous
      elif not node.previous:
        return True
      else:
        return False
  return False

def is_footer(soupnode, tolerance):
  """
  Returns "true" if the node matches an email client footer pattern
  Otherwise returns False

  Giveaway footers look often look something like this:

  <div class="gmail_quote">
  <div class="moz-signature">
  <blockquote>  > but we need to be a bit paranoid about this, you might legitimately be quoting someone
  <blockquote type="cite" cite="mid:4C988CBF.6000809@onlinegroups.net">  > we can be pretty sure about this one

  "On 22/09/2010, at 11:25 , Dan Randow wrote:"
  "On Dec 6, 2011, at 12:33 AM, Dan Randow wrote:"
  "----- Reply message -----"
  <br> --    \(at least 2)\

  From: bla bla bla
  To: Bla bla bla
  Sent (on):
    etc...
    In a variety of orders and markups.



  that is to say they could be strings OR tags OR a combo!
  """


  if isinstance(soupnode, BeautifulSoup.Tag):
    #start with the most obvious - do we have a known footer class
    if soupnode.get('class'):
      if soupnode['class'] in footer_classes:
        return True

    elif soupnode.name == 'blockquote':
      #ipad uses blockquote for inline replys as well as end of message quoting so we need to snoop the blockquote a bit.
      # lets see how many linebreaks there are. if lots then it can be snipped.
      if len(soupnode('br')) > tolerance['seek']:
        return True
      elif is_last(soupnode):
        return True
      else:
        return False

    elif soupnode.name == 'hr':
      if is_last(soupnode):
        return True

      #yahoo mail starts with hr then has some From: To: style stuff which we will make a bit more generic.
      i = 1

      while i < tolerance['seek']:
        if isinstance(soupnode.next, BeautifulSoup.NavigableString):
          if any(string in soupnode.next.upper().strip() for string in email_heads ):
            return True
          i += 1
        soupnode = soupnode.next

    else:
      return False

  elif isinstance(soupnode, BeautifulSoup.NavigableString):
    stripped_line = soupnode.string.strip()
    stripped_line_upper = stripped_line.upper()
    #If we get a certain number of &gt;'s in a row, we might have hit gold

    if stripped_line[:4] == '&gt;':
      #find the next br. If there's a &gt; right before it then we're got a run of 'em
      i = 1
      while i < tolerance['comment']:
        #find the node before the next br
        if soupnode.findNextSibling('br'):
          nextprev = soupnode.findNextSibling('br').previousSibling.string.strip()
          if nextprev[:4] == '&gt;':
            i+=1
          else:
            break
        else:
          break

      if i >= tolerance['comment'] :
        return True

    elif stripped_line_upper.startswith('----- REPLY') or ('--ORIGINAL MESSAGE--' in stripped_line_upper):
      #Generic reply text
      return True
    elif stripped_line_upper.startswith('ON') and ( stripped_line_upper[3:4].isdigit() or stripped_line_upper[3:6] in dates):
      # iOS mail style reply..  ON 23 DEC yourmom wrote:
      return True
    else:
      return False

  else:
    return False

def is_last(node):
  '''
  For added certainty, sometimes it's nice to know when you are the last significant thing on the page.
  returns True if the BeautifulSoup node fed to it has nothing after it in it's tree except br tags and empty lines
  '''

  safe_tail = False
  #trailing br tags and empty lines? we don't care about them.
  #make an array of all sibling nodes - probably this should be recursive back up the tree.
  tail = node.findNextSiblings()
  tail.extend(node.findNextSiblings(text = True))

  #nothing else in there besides br's and empty text nodes?
  if all( (isinstance(element, BeautifulSoup.Tag) and element.name=='br' )  or str(element).strip() == '' for element in tail):
    safe_tail = True


  #ok lets get down to business
  if not node.nextSibling or safe_tail:
    if not node.next:
      #ok then it really is the last one, in reality though node.next is likely to be a child of the last element
      return True

    #we need every object going to check if it's in the parent node
    children = node.findAll(text = True)
    children.extend(node.findAll())


    while node:
      if node.next in children:
        node  = node.next
      elif not node.next:
        return True
      else:
        return False


  return False

def is_signoff(element, tolerance):
  '''
  Takes the given element and does some sniffing arounf to try and determin if it represents the babble at the end of an email.
  This is fiendishly hard to identify as it containts things like
  'Cheers<br>Bob<br><br><a>bob@bob.com</a><br>0211 358 763 etc'

  we can't reliably pattern this, we can say it's a bunch of 1 or 2 word
  lines at the end of the message with <br>s and stuff everywhere
  So we'll walk the tree and see what we can find.

  param:  element. The BeautifulSoup element to start with
  param:  tolerance. The tolerance settings from split_html_message()
  return: False if nothing found, Otherwise a element representing where to _start_ the signoff
          Note, this might not be the element that was passed in if backtracking discovers something or we decide to extract the parent element.
  '''

  # It would be nice an efficient to walk backwards but man, it's a real pain
  # to figure out where you are. There could be no siblings because you are in a p tag
  # or simply because you are in the head.

  paranoiascore = 0 # we need to get a score >= tolerence['paranoia'] to make the call that this can be snipped

  # there are couple ways we could be in the snipping zone
  # 1 - a div or p containing multiple br's with a small amount of words (lots of siblings for each NavigableString)
  # 2 - a whole stack of p tags or divs (no siblings for each NavigableString except inline elements )
  # 3 - some sort of table (probably with images in it)  :|

  # First lets find a shortarse string.
  if isinstance(element, BeautifulSoup.NavigableString):

    wordcount = len(element.string.replace('&nbsp;' ,' ').split()) #nbsp's make 2 words look like one.
    if not (0 < wordcount <= tolerance['words_per_line']):
      #this just takes care of any OBVIOUSLY too long strings quickly.
      return False

    # ok we have a short string BUT consider this
    # <div>blah blah vdskjh sdkjusdjk dsjkias <a>hi there</a> blash bah </div>
    # we've got 2 strings with only 2 words in them there. Because of inline elements!
    # so we cant trust our current wordcount just yet...  Damnit :)
    # see get_line_length() for spaghetti

    start = element #lets keep the element var as is so we can refer to it later if we need to

    lineone  = get_line_length(start, tolerance)
    if lineone and 0 < lineone['count'] <= tolerance['words_per_line']:
      # ok, we have a legitimately short line  (<div><br><br></div> will have a length of 0)
      paranoiascore += 1

      for string in common_signoffs:
        if lineone['string'].strip().upper().startswith(string.upper()):
          #well, that's a pretty damn good sign but not a dead ringer for a footer.
          paranoiascore += tolerance['paranoia'] *.65

    # ok now lets fond the next meaningful line.
    if lineone['stop']:
      nextstring = get_line_length(lineone['stop'].next, tolerance)['stop']
      while isinstance(nextstring, BeautifulSoup.Tag) or (isinstance(nextstring, BeautifulSoup.NavigableString) and nextstring.strip() == ''):
        nextstring = nextstring.next

      linetwo = get_line_length(nextstring, tolerance)
      if linetwo and 0 < linetwo['count'] <= tolerance['words_per_line']:
        paranoiascore += 1
    else:
      # there was no stop! this means it's the bottom of the tree!
      paranoiascore += 1

    # get_position is expensive, so only run it if we arent already over the paranoia boundry
    if paranoiascore < tolerance['paranoia'] and get_position(start) > .75:
      paranoiascore += 1

    if paranoiascore >= tolerance['paranoia']:
      # ok looks like our paranoia is satiated.
      # 10 points for Gryffindor! That's a wrap, people.
      return start

  return False

def get_line_length(start, tolerance):
  '''
  Accepts an BeautifulSoup NavigableString and sniffs around all the other inline elements
  and strings to see how long the total line is
  Returns: a dict{
    count : int - the number of words
    stop  : BeautifulSoup object last word in the sequence. useful when you want to go on and check the next line
    string: the concatenated strings that were counted - good for debug
    }
  '''
    # walk left as long as elements remain inline OR strings till we run out OR hit a br
    # warning, uglyness follows:


  while start and not isinstance(start, BeautifulSoup.NavigableString):
    # if we are starting with a tag, dive for the first string (not recommended)
    start = start.next

  while True and start:
    if start.previousSibling and \
    isinstance(start.previousSibling, BeautifulSoup.Tag) and \
    (start.previousSibling.name == 'br' or (not start.previousSibling.name.upper() in inline_elements)):
      #print str(start) + ' has an inline sibling but it is evil: ' + str(start.previousSibling)
      break
    elif start.previousSibling:
      #print str(start) + ' has an inline sibling: ' + str(start.previousSibling)
      start = start.previousSibling

    elif start.previous and \
    isinstance(start.previous, BeautifulSoup.Tag) and \
    (start.previous.name == 'br' or (not start.previous.name.upper() in inline_elements)):
      #print str(start) + ' has an no sibling and prev element is evil: ' + str(start.previous)
      break
    elif start.previous:
      #print str(start) + ' has no sibling but prev element looks ok: ' + str(start.previous)
      start = start.previous
    else:
      #print str(start) + ' seems to be the first thing ever!'
      return False

  # ok now we have the start of the line (hopefully), we can walk back to the right looking for the stop or a br.
  stop = start
  shortlinewords = ''
  while stop:
    if isinstance(stop, BeautifulSoup.NavigableString) and \
    not stop.nextSibling and (not stop.parent.name.upper() in inline_elements):
      # deal with the common single string in a block element <div>hey guys</div>
      shortlinewords += stop.strip() + ' '
      break
    elif isinstance(stop, BeautifulSoup.NavigableString):
      shortlinewords += stop.strip() + ' '
      stop = stop.next
    elif isinstance(stop, BeautifulSoup.Tag) and \
    (stop.name == 'br' or (not stop.name.upper() in inline_elements)):
      break
    elif isinstance(stop, BeautifulSoup.Tag):
      stop = stop.next
    else:
      return False

  length = len(shortlinewords.split())
  return {'count' : length , 'string' : shortlinewords, 'stop' : stop }

def get_position(node):
  '''
  returns a decimal <= 1 representing how far thorough the tree the node is.
  param: node - a BeautifulSoup node object
  '''
  top = node
  i = 0
  #quickly jump up the tree
  while top.parent:
    top = top.parent
  while top.previousSibling:
    top = top.previousSibling

  top = top.contents[0]
  while top:
    i += 1
    if top == node:
      position = i
    top = top.next

  # print type(position)
  # print type(i)

  return float(position) / float(i)

def strip_trailing_rubbish(dom):
  '''
  remove any trailing empty tags. and whitespace.
  param: dom, the Erroneously named BeautifulSoup tree or part thereof
  return: the same tree with trailing rubbish removed
  '''
  node = dom.contents[0]
  while node.next:
    # get the last element
    node = node.next

  while True:
    if isinstance(node, BeautifulSoup.Tag) and node.name == 'br':
      #print str(node) + ' is br'
      prev = node.previous
      node.extract()
      node = prev
    elif isinstance(node, BeautifulSoup.Tag) and \
    (node.name == 'div' or node.name == 'p') and \
    (not node.contents) or \
    (str(node) is None or not str(node).strip()):


      #print str(node) + ' is empty tag
      prev = node.previous
      node.extract()
      node = prev
    else:
      break

  return dom

def strip_empty_tags(dom):
  '''
  Empty tags arent doing anything for anyone, lets get rid of them
  Returns html tree minus tags that are found to contain nothing but whitespace
  '''
  while True:
    element = dom.contents[0]
    extracted = 0
    while element:
      if isinstance(element, BeautifulSoup.Tag):
        if element.name in BeautifulSoup.BeautifulSoup.SELF_CLOSING_TAGS:
          # Self closing tags have no content but we want to keep them.
          pass
        elif not element.contents or \
        (len(element.contents) == 1 and element.contents[0].strip == '') and \
        (element.string is None or not element.string.strip()):
          # else if there's nothing in it but whitespace...
          element.extract()
          extracted += 1
      element = element.next

    if extracted == 0:
      # rinse and repeat till we have them all
      break
  return dom

####################################################
#testing rubbish

def runall():
  rawdir = 'html-email-corpus/'
  cleandir = 'scrubbed-html-email-corpus/'
  listing = os.listdir( rawdir )

  for infile in listing:
    print infile
    #print infile
    f = open( rawdir+infile, 'r' )
    n = open (cleandir+infile, 'a')
    n.truncate(0)

    message = split_html_message(f.read())
    n.write(message[0])
    n.write("<div>-------------------------------</div>")
    n.write(message[1])
    f.close()
    n.close()


def runone():
  file = 'canterburyissues-hotmail-quote.html'
  #file = 'testlast.html'



  f = open('html-email-corpus/'+file , 'r')
  n = open ('scrubbed-html-email-corpus/'+file, 'a')
  n.truncate()

  message = split_html_message(f.read())

  n.write(message[0])
  n.write("<div>-------------------------------</div>")
  n.write(message[1])


  f.close()
  n.close()

runall()
