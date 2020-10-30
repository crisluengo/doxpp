#ifndef __TRANSPORT_RACING_BIKE_H__
#define __TRANSPORT_RACING_BIKE_H__

#include <transport/bicycle.hh>

/// \file
/// Defines the `RacingBike` class

/// \addtogroup bikes

/// The first line here should be ignored, because the brief is defined in a header parsed earlier
/// But this is some additional documentation for this namespace that we add to the bottom
/// of the previously written documentation. The order depends on the order in which files are
/// parsed!
namespace transport
{
	/** Racing bike class.
	 *
	 * `RacingBike` is a special kind of bike which can go much faster
	 * on the road, with much less effort (even uphill!). It doesn't make
	 * sense to call \ref RingBell on a racing bike for they don't have bells.
	 */
	class RacingBike : public Bicycle
	{
	public:
		/** @inherit */
		virtual void PedalHarder();

		/** `RingBell` is not implemented. */
		virtual void RingBell();

		/// What kind of gears can a `RacingBike` have?
		enum class GearSystem {
		   expensive, ///< These are the good gears, or maybe they're just overpriced
		   cheap      ///< These gears won't last long
		};

		/// What kind of gears does this racing bike have?
		GearSystem gearSystem = GearSystem::expensive;
	};
}

/// \endgroup

#endif /* __TRANSPORT_RACING_BIKE_H__ */
