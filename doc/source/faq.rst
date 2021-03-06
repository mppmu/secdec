Frequently Asked Questions
==========================

How can I adjust the integrator parameters?
-------------------------------------------

If the python interface is used for the numerical integration, i.e. a python script like ``examples/integrate_box1L.py``, the integration parameters can be specified in the argument list of the integrator call.
For example, using Vegas as integrator::

    box1L.use_Vegas(flags=2, epsrel=1e-3, epsabs=1e-12, nstart=5000, nincrease=10000, maxeval=10000000, real_complex_together=True)

Or, using Divonne as integrator::

    box1L.use_Divonne(flags=2, epsrel=1e-3, epsabs=1e-12, maxeval=10000000, border=1e-8, real complex together=True)

The parameter real complex together tells the integrator to integrate real and imaginary parts simultaneously. A complete list of possible options for the integrators can be found in :mod:`integral_interface <pySecDec.integral_interface>`.

If the C++ interface is used, the options can be specified as fields of the integrator.
For example, after running ``examples/generate_box1L.py``, in the file ``examples/box1L/integrate_box1L.cpp``, you can modify the corresponding block to e.g.::

    // Integrate
    secdecutil::cuba::Vegas<box1L::integrand_return_t> integrator;
    integrator.flags = 2; // verbose output --> see cuba manual
    integrator.epsrel = 1e-2;
    integrator.epsabs = 1e-12;
    integrator.nstart = 5000;
    integrator.nincrease = 10000;
    integrator.maxeval = 10000000;
    integrator.together = true;

In order to set the Divonne integrator with the same parameters as above, do::

    // Integrate
    secdecutil::cuba::Divonne<box1L::integrand_return_t> integrator;
    integrator.flags = 2; // verbose output --> see cuba manual
    integrator.epsrel = 1e-2;
    integrator.epsabs = 1e-12;
    integrator.maxeval = 10000000;
    integrator.border = 1e-8;
    integrator.together = true;

More information about the C++ integrator class can be found in :numref:`chapter_secdecutil_integrator`.

How can I request a higher numerical accuracy?
----------------------------------------------

The integrator stops if any of the following conditions is fulfilled: (1) ``epsrel`` is reached, (2) ``epsabs`` is reached, (3) ``maxeval`` is reached.
Therefore, setting these parameters accordingly will cause the integrator to make more iterations and reach a more accurate result.

How can I tune the contour deformation parameters?
--------------------------------------------------

You can specify the parameters in the argument of the integral call in the python script for the integration, see e.g. line 12 of ``examples/integrate box1L.py``::

    str_integral_without_prefactor, str_prefactor, str_integral_with_prefactor=box1L(real_parameters=[4.,-0.75,1.25,1.],number_of_presamples=10**6,deformation_parameters_maximum=0.5)

This sets the number of presampling points to ``10**6`` (default: ``10**5``) and the maximum value for the contour deformation parameter ``deformation_parameters_maximum`` to ``0.5`` (default: ``1``). The user should make sure that deformation parameters maximum is always larger than deformation_parameters_minimum (default: ``1e-5``). These parameters are described in :class:`IntegralLibrary <pySecDec.integral_interface.IntegralLibrary>`.

What can I do if the program stops with an error message containing `sign_check_error`?
---------------------------------------------------------------------------------------

This error occurs if the contour deformation leads to a wrong sign of the Feynman :math:`i\delta` prescription, usually due to the fact that the deformation parameter :math:`\lambda` is too large. Choose a larger value for ``number_of_presamples`` and a smaller value (e.g. ``0.5``) for ``deformation_parameters_maximum`` (see item above). If that does not help, you can try ``0.1`` instead of ``0.5`` for ``deformation_parameters_maximum``. The relevant parameters are described in :class:`IntegralLibrary <pySecDec.integral_interface.IntegralLibrary>`.

What does `additional_prefactor` mean exactly?
----------------------------------------------

We should first point out that the conventions for additional prefactors defined by the user have been changed between `SecDec 3` and `pySecDec`. The prefactor specified by the user will now be *included* in the numerical result.

To make clear what is meant by "additional", we repeat our conventions for Feynman integrals here.

A scalar Feynman graph :math:`G` in :math:`D` dimensions at :math:`L` loops with :math:`N` propagators, where the propagators can have arbitrary, not necessarily integer powers :math:`\nu_j`, has the following representation in momentum space:

.. math::
   :nowrap:

    \begin{align}
    G &= \int\prod\limits_{l=1}^{L} \mathrm{d}^D\kappa_l\;
    \frac{1}
    {\prod\limits_{j=1}^{N} P_{j}^{\nu_j}(\{k\},\{p\},m_j^2)}, \nonumber \\
    \mathrm{d}^D\kappa_l&=\frac{\mu^{4-D}}{i\pi^{\frac{D}{2}}}\,\mathrm{d}^D k_l\;,\;
    P_j(\{k\},\{p\},m_j^2)=(q_j^2-m_j^2+i\delta)\;, \nonumber
    \end{align}

where the :math:`q_j` are linear combinations of external momenta :math:`p_i` and loop momenta :math:`k_l`.

Introducing Feynman parameters leads to:

.. math::

    G = (-1)^{N_{\nu}}
    \frac{\Gamma(N_{\nu}-LD/2)}{\prod_{j=1}^{N}\Gamma(\nu_j)}\int
    \limits_{0}^{\infty}
    \,\prod\limits_{j=1}^{N}dx_j\,\,x_j^{\nu_j-1}\,\delta(1-\sum_{l=1}^N x_l)\,\frac{{\cal U}^{N_{\nu}-(L+1) D/2}}
    {{\cal F}^{N_\nu-L D/2}}

The prefactor :math:`(-1)^{N_{\nu}}\,\Gamma(N_{\nu}-LD/2)/\prod_{j=1}^{N}\Gamma(\nu_j)` coming from the Feynman parametrisation will always be included in the numerical result, corresponding to `additional_prefactor=1` (default), i.e. the program will return the numerical value for :math:`G`. If the user defines `additional_prefactor='gamma(3-2*eps)'`, this prefactor will be expanded in :math:`\epsilon` and included in the numerical result returned by `pySecDec`, in addition to the one coming from the Feynman parametrisation.

For general polynomials not related to loop integrals, i.e. in ``make_package``, the prefactor provided by the user is the only prefactor, as there is no prefactor coming from a Feynman parametrisation in this case. This is the reason why in :func:`make_package <pySecDec.code_writer.make_package>` the keyword for the prefactor defined by the user is ``prefactor``, while in :func:`loop_package <pySecDec.loop_integral.loop_package>` it is ``additional_prefactor``.


What can I do if I get `nan`?
-----------------------------

This means that the integral does not converge which can have several reasons. When Divonne is used as an integrator, it is important to use a non-zero value for border, e.g. ``border=1e-8``. Vegas is in general the most robust integrator. When using Vegas, try to increase the values for ``nstart`` and ``nincrease``, for example ``nstart=100000`` (default: ``10000``) and ``nincrease=50000`` (default: ``5000``).

If the integral is non-Euclidean, make sure that `contour_deformation=True` is set.
Another reason for getting `nan` can be that the integral has  singularities at :math:`x_i = 1` and therefore needs usage of the ``split`` option, see item below.

What can I use as numerator of a loop integral?
-----------------------------------------------

The numerator must be a sum of products of numbers, scalar products (e.g. ``p1(mu)*k1(mu)*p1(nu)*k2(nu)`` and/or symbols (e.g. ``m``). The numerator can also be an inverse propagator.
In addition, the numerator must be finite in the limit :math:`\epsilon \rightarrow 0`. The default numerator is ``1``.

Examples::

    p1(mu)*k1(mu)*p1(nu)*k2(nu) + 4*s*eps*k1(mu)*k1(mu)
    p1(mu)*(k1(mu) + k2(mu))*p1(nu)*k2(nu)
    p1(mu)*k1(mu)

More details can be found in :class:`LoopIntegralFromPropagators <pySecDec.loop_integral.LoopIntegralFromPropagators>`.


How can I integrate just one coefficient of a particular order in the regulator?
--------------------------------------------------------------------------------

You can pick a certain order in the C++ interface (see :ref:`cpp_interface`). To integrate only one order, for example the finite part, change the line::

    const box1L::nested_series_t<secdecutil::UncorrelatedDeviation<box1L::integrand_return_t>> result_all = secdecutil::deep_apply( all_sectors, integrator.integrate );

to::

    int order = 0; // compute finite part only
    const secdecutil::UncorrelatedDeviation<box1L::integrand_return_t> result_order = secdecutil::deep_apply(all_sectors.at(order), integrator.integrate );

where ``box1L`` is to be replaced by the name of your integral. In addition, you should change the lines::

    std::cout << "-- integral without prefactor -- " << std::endl;
    std::cout << result_all << std::endl << std::endl;

to::

    std::cout << "-- integral without prefactor -- " << std::endl;
    std::cout << result_order << std::endl << std::endl;

and remove the lines::

    std::cout << "-- prefactor -- " << std::endl;
    const box1L::nested_series_t<box1L::integrand_return_t> prefactor = box1L::prefactor(real_parameters, complex_parameters);
    std::cout << prefactor << std::endl << std::endl;

    std::cout << "-- full result (prefactor*integral) -- " << std::endl;
    std::cout << prefactor*result_all << std::endl;

because the expansion of the prefactor will in general mix with the pole coefficients and thus affect the finite part. We should point out however that deleting these lines also means that the result will not contain any prefactor, not even the one coming from the Feynman parametrisation.

How can I use complex masses?
-----------------------------

In the python script generating the expressions for the integral, define mass symbols in the same way as for real masses, e.g::

    Mandelstam_symbols=['s']
    mass_symbols=['msq']

Then, in :mod:`loop_package <pySecDec.loop_integral.loop_package>` define::

    real parameters = Mandelstam_symbols,
    complex parameters = mass_symbols,

In the integration script (using the python interface), the numerical values for the complex parameters are given after the ones for the real parameters::

    str_integral_without_prefactor, str_prefactor, str_integral_with_prefactor = integral(real_parameters=[4.],complex_parameters=[1.-0.0038j])

Note that in python the letter ``j`` is used rather than ``i`` for the imaginary part.

In the C++ interface, you can set (for the example `triangle2L`)::

    const std::vector<triangle2L::real_t> real_parameters = { 4. };
    const std::vector<triangle2L::complex_t> complex_parameters = { {1.,0.0038} };


When should I use the “split” option?
-------------------------------------

The modules :func:`loop_package <pySecDec.loop_integral.loop_package>` and :func:`make_package <pySecDec.code_writer.make_package>` have the option to split the integration domain (``split=True``). This option can be useful for integrals which do not have a Euclidean region. If certain kinematic conditions are fulfilled, for example if the integral contains massive on-shell lines, it can happen that singularities at :math:`x_i = 1` remain in the :math:`\mathcal{F}` polynomial after the decomposition. The split option remaps these singularities to the origin of parameter space. If your integral is of this type, and with the standard approach the numerical integration does not seem to converge, try the ``split`` option. It produces a lot more sectors, so it should not be used without need. We also would like to mention that very often a change of basis to increase the (negative) power of the :math:`\mathcal{F}` polynomial can be beneficial if integrals of this type occur in the calculation.

