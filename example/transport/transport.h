#ifndef __TRANSPORT_H__
#define __TRANSPORT_H__

/// \file
/// Main include file for the `transport` project
/// This is the longer documentation...

#include <transport/bicycle.h>
#include <transport/racingbike.h>
#include <transport/mountainbike.h>

#include <array>
#include <string>
#include <list>

/// quee namespace
namespace quee {
/// acho type
using acho = unsigned int;
}

/// fruns type
template<typename T>
using fruns = std::array<T, 5>;

/// muyk type
typedef fruns<size_t> muyk;

/// foo function
std::list<std::string> foo();

/// class Antox
template<typename Bexta = quee::acho>
class Antox {
public:
   /// conversion operator
   operator quee::acho const&();

   /// some function
   void pluka(quee::acho& a, double d);

   /// a templated function
   template<typename T>
   fruns<T>& wakati(fruns<T>& t);

   /// our type
   using Type = Bexta;
};

/// complex template reference
using xuptip = std::list<Antox<fruns<int>>::Type>;

/// a function that takes a function pointer
void malar(int(*comparator)(xuptip a, Antox<fruns<int>> b));

#endif /* __TRANSPORT_H__ */
