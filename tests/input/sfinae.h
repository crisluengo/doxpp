#include <type_traits>
#include <limits>

/// A struct template that can only be instantiated for types that can represent infinity.
template< typename A, typename std::enable_if< !std::numeric_limits< A >::has_infinity, int >::type = 0 >
struct S {
   A member;
};
