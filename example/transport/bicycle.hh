#ifndef __TRANSPORT_BICYCLE_H__
#define __TRANSPORT_BICYCLE_H__

#include <string>

///
/// \file
/// \brief Defines the `Bicycle` class
///
/// This is a pretty sweet file all by itself, but the `Bicycle` class is virtual,
/// so this file is even better when combined with other files that define derived
/// classes.

/// The namespace for the project
namespace transport
{
   /// A string
   using str = std::string;
   /// Another string
   typedef str foo;

	/** \brief Standard bicycle class. This is a rather long brief line, it
	 * occupies the whole paragraph...
	 *
	 * Bicycle implements a standard bicycle. Bicycles are a useful way of
	 * transporting oneself, without too much effort (unless you go uphill
	 * or against the wind). If there are a lot of people on the road, you
	 * can use <RingBell> to ring your bell (**note**, not all bicycles
	 * have bells!).
	 */
	class Bicycle
	{
	public:
		/// PedalHarder makes you go faster (usually).
		// this is a regular comment, not for documentation
		virtual void PedalHarder();

		/** Ring bell on the bike.
		 *
		 * RingBell rings the bell on the bike. Note that not all
		 * bikes have bells. */
		virtual void RingBell();

		/// Default destructor.
		///
		/// Some might want to override this
		virtual ~Bicycle();

	private:
	   int id; ///< Something to identify a bike by
	};
}

#endif /* __TRANSPORT_BICYCLE_H__ */
