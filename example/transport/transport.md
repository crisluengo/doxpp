\comment This produces some documentation pages, and adds documentation to some
\comment stuff in the header files.

\mainpage This is the index!
This project is called 'transport', and defines some classes named after types
of bicycles.

A good place to start looking is examining the \ref transport namespace.

\ref transport "This whole sentence is a reference to the transport namespace!" 

Here's some more stuff to read: \subpage page1


\page page1 This is another page
Let's add some references to members of the \ref transport namespace:

- \ref transport::Bicycle is the base class
- \ref transport::MountainBike is a derived class
- \ref transport::RacingBike is the other derived class

These are two different functions, with the same name. They're overloads!

- \ref transport::ComplexStructTemplate::ComplexStructTemplate(const ComplexStructTemplate&)
- \ref transport::ComplexStructTemplate::ComplexStructTemplate(ComplexStructTemplate &&)

Note that we can reference multiple things one one line: \ref transport::foo, \ref transport::bar.

\ref transport::ComplexStructTemplate::ComplexStructTemplate(const ComplexStructTemplate&) \ref transport::ComplexStructTemplate::ComplexStructTemplate(ComplexStructTemplate &&).

\class transport::Bicycle
\brief this is ignored

But here's some additional documentation for the `Bicycle` class.
