#include <new>

/** Namespace N
 * Contains \ref "operator==", and \ref "operator""_w", as well as struct \ref A.
 *
 * We should be able to reference \ref "operator==" or \ref "operator==(const A &, const A &)"
 */
namespace N
{
   /** Struct N::A
    * Contains \ref "operator<", and \ref "operator int*".
    */
   struct A
   {
      bool operator<(const A &other);
      operator int*() const;
   };

   /// operator==
   bool operator==(const A &a, const A &b);

   /// operator "" _w() allows us to write `34.5_w` to create an object of type \ref A.
   A operator "" _w(long double);
}

void* operator new(std::size_t);
void* operator new [](std::size_t);
void operator delete(void*) noexcept;
void operator delete [](void*) noexcept;
