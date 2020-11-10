#ifndef __TRANSPORT_MOUNTAIN_BIKE_H__
#define __TRANSPORT_MOUNTAIN_BIKE_H__

#include <transport/bicycle.h>
#include <type_traits>

/// \file
/// Defines the `MountainBike` class

/// \addtogroup bikes

namespace transport
{

   /// \defgroup all-terrain All-terrain bicycles
   /// A group of classes representing bicycle types that can go off-road

   /** Mountain bike implementation of a \ref Bicycle.
    *
    * `MountainBike` is an implementation of a \ref Bicycle
    * providing a bike for cycling on rough terrain. Mountain bikes
    * are pretty cool because they have stuff like **Suspension** (and
    * you can even adjust it using \ref SetSuspension). If you're looking
    * for a bike for use on the road, you might be better off using a
    * \ref RacingBike though.
    */
   class MountainBike : public Bicycle
   {
   public:
      /** Set suspension stiffness.
       * @param stiffness the suspension stiffness.
       *
       * `SetSuspension` changes the stiffness of the suspension
       * on the bike. The method will return false if the stiffness
       * could not be adjusted.
       *
       * @return true if the suspension was adjusted successfully,
       *         false otherwise.
       */
      bool SetSuspension(const double stiffness = 0);

      /** Change the break type.
       * @tparam BreakType the break type.
       * @param breakType the type of the break.
       *
       * `ChangesBreak` changes the type of break fitted to the bike.
       * The method will return false if the break type could not be
       * fitted.
       *
       * @return true if the break was adjusted successfully.
       *         false otherwise
       */
      template <typename BreakType>
      bool ChangeBreak(const BreakType breakType) {
         if (breakType) {
            return true;
         }
         return false;
      }
   };

   /// \endgroup

/// For some reason, this definition takes the documentation for the declaration, ignoring this.
bool MountainBike::SetSuspension(const double stiffness) {}

/// A constexpr declaration
/// \relates MountainBike
static constexpr int CONST = 5;

}

/// \endgroup

#endif /* __TRANSPORT_MOUNTAIN_BIKE_H__ */
