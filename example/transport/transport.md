\comment This produces some documentation pages, and adds documentation to some
\comment stuff in the header files.


\mainpage This is the index!
This project is called 'transport', and defines some classes named after types
of bicycles.

A good place to start looking is examining the \ref transport namespace.\anchor anchor-in-main

\ref transport "This whole sentence is a reference to the transport namespace!" 

Here's some more stuff to read: \subpage page1

\section main-test-refs Testing references

The main header file is \ref file--transport--transport-h. There's also \ref "transport/racingbike.h" as well
as \ref "mountainbike.h"!

\subsection main-test-refs-sa ... in  a "See also" block

\see file--transport--transport-h, "transport/racingbike.h", "mountainbike.h"


\comment ----------------------
\comment --- This is page1: ---
\comment ----------------------

\page page1 This is another page
Let's add some references to members of the \ref transport namespace:

- \ref transport::Bicycle is the base class
- \ref transport::MountainBike is a derived class
- \ref transport::RacingBike is the other derived class

Here we reference specific versions of overloaded methods:

- \ref transport::RacingBike::PedalHarder()
- \ref transport::RacingBike::PedalHarder(double)

We can reference the first one of the two using this ambiguous reference:
\ref transport::RacingBike::PedalHarder. Note that we can reference
multiple things one one line: \ref transport::foo, \ref macro--FOOBAR.

\see transport::Bicycle, transport::MountainBike, transport::RacingBike, transport::RacingBike::PedalHarder(double), transport::RacingBike::PedalHarder(), transport::foo, macro--FOOBAR

We can reference back to \ref index "the main page" right here, but also to random
anchors in it, for example \ref anchor-in-main "this one" or \ref main-test-refs-sa.
Here is a reference to an anchor in the documentation to `transport::Bicycle`:
\ref anchor-bicycle.

\comment ------------------------------------------------------------------------
\comment --- This is additional documentation for class `transport::Bicycle`: ---
\comment ------------------------------------------------------------------------

\class transport::Bicycle
\brief this is ignored

But here's some additional documentation for the `Bicycle` class. \anchor anchor-bicycle
