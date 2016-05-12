Changelog
=========

1.1.2 (2016-05-12)
------------------

* Fixing a coding error regarding mutable data-types as
  parameters

1.1.1 (2015-11-12)
------------------

* Closing an anchor tag

1.1.0 (2015-10-30)
------------------

* Allowing the support email-address and group email-address to
  be seen in posts made to public groups
* Updating the documentation
* Moving the ``split_message`` function to `gs.group.messages.text`_
* Moving the ``Matcher`` classes to `gs.group.messages.text`_
* Adding unit tests

.. _gs.group.messages.text:
   https://github.com/groupserver/gs.group.messages.text

1.0.2 (2015-10-22)
------------------

* Leaving the *closing* (such as “Yours sincerely…” or “Kind
  regards…”) in the main body of the message
  <http://groupserver.org/r/topic/2aoyDWJ8tYel6UUQkpPnM>

1.0.1 (2015-10-21)
------------------

* Snipping bottom quoting caused by Mozilla Thunderbird when it
  converts the HTML-formatted version of a post to plain text —
  including dumping the contents of the ``<style>`` elements into
  the message
* Tweaking the bottom-quoting code so very short closings remain
  visible
* Switching the viewlet to use the correct form of the message
* Added unit tests for the ``split_message`` function
* Updated the ``split_message`` function to use
  `collections.namedtuple`_, `collections.deque`_, `enumerate`_
  and `conditional-expressions`_

.. _collections.namedtuple:
   https://docs.python.org/2.7/library/collections.html#collections.namedtuple

.. _collections.deque:
   https://docs.python.org/2.7/library/collections.html#collections.deque

.. _enumerate:
   https://docs.python.org/2.7/library/functions.html#enumerate

.. _conditional-expressions:
   https://docs.python.org/2.7/reference/expressions.html#conditional-expressions

1.0.0 (2015-10-14)
------------------

Initial version. Prior to the creation of this product the
plain-text version of the posts were rendered by
`gs.group.messages.post.base`_. Originally (circa 2007) they were
rendered by the ZMI-side scripts in the folder
``Presentation/Tofu/MailingListManager/lscripts`` (list-scripts).

.. _gs.group.messages.post.base:
   https://github.com/groupserver/gs.group.messages.post.base

..  LocalWords:  Changelog iframe
