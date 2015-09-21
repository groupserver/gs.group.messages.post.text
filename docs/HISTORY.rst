Changelog
=========

3.4.4 (2015-09-21)
------------------

* Using ``subject`` rather than ``Subject`` in ``mailto:`` URIs

3.4.3 (2015-07-24)
------------------

* Hitting code with the PEP-8 stick 

3.4.2 (2015-04-16)
------------------

* Switching from ``<object>`` to ``<iframe>`` for YouTube and
  Vimeo videos

3.4.1 (2015-03-11)
------------------

* [FR] Adding a French translation, thanks to `Razique Mahroua`_

.. _Razique Mahroua:
   https://www.transifex.com/accounts/profile/Razique/

3.4.0 (2015-02-27)
------------------

* Naming the reStructuredText files as such
* Switching to GitHub_ as the canonical repository
* Adding internationalisation support
* Adding support for Transifex_

.. _GitHub: https:/github.com/groupserver/gs.group.messages.post/
.. _Transifex:
   https://www.transifex.com/projects/p/gs-group-messages-post/

3.3.0 (2014-06-11)
------------------

* Hiding the email address only when Anonymous can see the
  address
* Using the ``GroupVisibility`` code for displaying the privacy
  information

3.2.2 (2014-03-17)
------------------

* Following some new changes to the *Sharebox*
* Using ``strict`` mode in the JavaScript
* Switching to Unicode literals

3.2.1 (2013-12-06)
------------------

* Switching to the new *Loading* icon

3.2.0 (2013-11-15)
------------------

* Following the new *Sharebox* code
* Metadata update
* Fixing some more whitespace

3.1.2 (2013-07-31)
------------------

* Fixing some minor white-space

3.1.1 (2013-06-06)
------------------

* Minifying the JavaScript code

3.1.0 (2013-04-05)
------------------

* Adding icons for files, the navigation links, and breadcrumb
  trail

3.0.0 (2013-03-22)
------------------

* Updating the *Post* page for the new GroupServer user interface

  + Reformatting the files
  + Switching to Twitter Bootstrap for the *Hide* and *Share*
    interfaces
  + Adding a breadcrumb trail
  + Adding WAI-ARIA markup

* General PEP-8 code cleanup

2.0.1 (2012-10-10)
------------------

* Adding a post-date index

2.0.0 (2012-09-21)
------------------

* Switching to use the PostgreSQL full-text retrieval vector for
  searching

1.5.0 (2012-07-18)
------------------

* Refactoring the post code to allow ``can_hide_post`` to be
  overridden

1.4.0 (2012-06-28)
------------------

* Updating the ``gs.database`` code
* Updating SQLAlchemy
* Updating the cache code
* Fixing the hide-a-post query

1.3.0 (2012-05-16)
------------------

* Handling the new ``youtu.be`` URLs

1.2.0 (2011-09-28)
------------------

* Changing the name of the *Hide post* button, and the *Rest of
  post* button.

1.1.2 (2011-05-06)
------------------

* Fixing a problem with long URLs

1.1.1 (2011-04-29)
------------------

* Hiding the hide link when the member cannot hide the post
* Fixing some SQL problems

1.1.0 (2011-04-21)
------------------

* Adding a user-interface for hiding a post

1.0.1 (2011-04-05)
------------------

* Adding back-end support for hidden posts
* Improving the performance

1.0.0 (2011-02-21)
------------------

Initial version. Prior to the creation of this product the posts
were rendered by ``Products.XWFMailingListManager``.

..  LocalWords:  Changelog iframe
