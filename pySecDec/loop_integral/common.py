"""Routines to Feynman parametrize a loop integral"""

from ..algebra import Polynomial, ExponentiatedPolynomial
from ..misc import cached_property, sympify_symbols, assert_degree_at_most_max_degree
import sympy as sp
import numpy as np
from math import floor

class LoopIntegral(object):
    r'''
    Container class for loop integrals.
    The main purpose of this class is to convert a
    loop integral from the momentum representation
    to the Feynman parameter representation.

    It is possible to provide either the graph
    of the loop integrals as adjacency list,
    or the propagators.

    The Feynman parametrized integral is a product
    of the following expressions that are accessible
    as member properties:

    * ``self.regulator ** self.regulator_power``
    * ``self.Gamma_factor``
    * ``self.exponentiated_U``
    * ``self.exponentiated_F``
    * ``self.numerator``
    * ``self.measure``,

    where ``self`` is an instance of either
    :class:`.LoopIntegralFromGraph` or
    :class:`.LoopIntegralFromPropagators`.

    When inverse propagators or nonnumerical propagator
    powers are present (see `powerlist`), some
    `Feynman_parameters` drop out of the integral. The
    variables to integrate over can be accessed as
    ``self.integration_variables``.

    While ``self.numerator`` describes the numerator
    polynomial generated by tensor numerators or inverse
    propagators, ``self.measure`` contains the monomial
    associated with the integration measure in the case
    of propagator powers :math:`\neq 1`. The Gamma functions
    in the denominator belonging to the measure, however,
    are multiplied to the overall Gamma factor given by
    ``self.Gamma_factor``. The overall sign
    :math:`(-1)^{N_\nu}` is included in ``self.numerator``.

    .. seealso::
        * input as graph: :class:`.LoopIntegralFromGraph`
        * input as list of propagators: :class:`.LoopIntegralFromPropagators`

    '''
    def __init__(self, *args, **kwargs):
        raise AttributeError('Use one of the derived classes.')

    @cached_property
    def exponent_U(self):
        return self.N_nu - self.U_derivatives - self.dimensionality / 2 * (self.L + 1)\
            - self.highest_rank

    @property # not cached on purpose --> this is just making copies
    def exponentiated_U(self):
        return ExponentiatedPolynomial(self.U.expolist, self.U.coeffs, self.exponent_U, self.U.polysymbols)

    @cached_property
    def exponent_F(self):
        return self.dimensionality / 2 * self.L - (self.N_nu + self.F_derivatives)

    @property # not cached on purpose --> this is just making copies
    def exponentiated_F(self):
        return ExponentiatedPolynomial(self.F.expolist, self.F.coeffs, self.exponent_F, self.F.polysymbols)

    common_properties_doc = r'''
    :param replacement_rules:
        iterable of iterables with two strings or sympy
        expressions, optional;
        Symbolic replacements to be made for the external
        momenta, e.g. definition of Mandelstam variables.
        Example: [('p1*p2', 's'), ('p1**2', 0)] where
        ``p1`` and ``p2`` are external momenta.
        It is also possible to specify vector replacements,
        for example [('p4', '-(p1+p2+p3)')].

    :param Feynman_parameters:
        iterable or string, optional;
        The symbols to be used for the Feynman parameters.
        If a string is passed, the Feynman parameter
        variables will be consecutively numbered starting
        from zero.

    :param regulator:
        string or sympy symbol, optional;
        The symbol to be used for the dimensional regulator
        (typically :math:`\epsilon` or :math:`\epsilon_D`)

        .. note::
            If you change this symbol, you have to adapt
            the `dimensionality` accordingly.

    :param regulator_power:
        integer;
        The regulator to this power will be multiplied by
        the numerator.

    :param dimensionality:
        string or sympy expression, optional;
        The dimensionality; typically :math:`4-2\epsilon`,
        which is the default value.

    :param powerlist:
        iterable, optional;
        The powers of the propergators, possibly dependent on
        the `regulator`. In case of negative powers, the
        derivative with respect to the corresponding Feynman
        parameter is calculated as explained in Section 3.2.4
        of Ref. [BHJ+15]_. If negative powers are combined with
        a tensor numerator, the derivative acts on the
        Feynman-parametrized tensor numerator as well, which
        should lead to a consistent result.

    '''
    #TODO: Prove last statement in description of powerlist, then replace `should lead` by `leads`

    def set_common_properties(self, replacement_rules, Feynman_parameters, regulator, regulator_power,
                              dimensionality, powerlist):
        # sympify and store `regulator`
        self.regulator = sympify_symbols([regulator], '`regulator` must be a symbol.')[0]

        # check and store `regulator_power`
        regulator_power_as_int = int(regulator_power)
        assert regulator_power_as_int == regulator_power, '`regulator_power` must be integral.'
        self.regulator_power = regulator_power_as_int

        # sympify and store `dimensionality`
        self.dimensionality = sp.sympify(dimensionality)

        # check and store replacement rules
        if not isinstance(replacement_rules, list):
            replacement_rules = list(replacement_rules)
        if replacement_rules:
            self.replacement_rules = np.array(replacement_rules)
            assert len(self.replacement_rules.shape) == 2, "The `replacement_rules` should be a list of tuples"
            assert self.replacement_rules.shape[1] == 2 , "The `replacement_rules` should be a list of tuples"
            for rule in self.replacement_rules:
                for expression in rule:
                    assert_degree_at_most_max_degree(expression, self.all_momenta, 2, 'Each of the `replacement_rules` must be polynomial and at most quadratic in the momenta.')
        else:
            self.replacement_rules = []

        # sympify and store `Feynman_parameters`
        # There should be one Feynman parameter for each propagator.
        if isinstance(Feynman_parameters, str):
            self.Feynman_parameters = [sp.sympify(Feynman_parameters + str(i)) for i in range(self.P)]
        else:
            self.Feynman_parameters = sp.sympify(list(Feynman_parameters))
            assert len(self.Feynman_parameters) == self.P, \
                'Mismatch between the number of `propagators` (%i) and the number of `Feynman_parameters` (%i)' % \
                ( len(self.propagators) , len(self.Feynman_parameters) )

        # check and store `powerlist`
        # If there are negative powers, determine the number of derivatives neseccary to make them positive
        # and store them in derivativelist.
        if not powerlist:
            self.powerlist = [sp.sympify(1)] * self.P
            self.derivativelist = [0] * self.P
            self.number_of_derivatives = 0
        else:
            assert len(powerlist)==self.P, "The length of the powerlist must equal the number of propagators."

            self.powerlist=[]
            self.derivativelist=[]

            for power in powerlist:
                power_sp = sp.sympify(power)
                power0 = power_sp.subs(regulator,0)
                assert power0.is_Number, "The propagator powers must be numbers for vanishing regulator."
                # TODO: how to treat integrable divergencies (0<power0<1)?
                self.powerlist.append(power_sp)
                if power0.is_positive:
                    self.derivativelist.append(0)
                else:
                    self.derivativelist.append(int(abs(floor(power0))))

            self.number_of_derivatives = sum(self.derivativelist)

        self.U_derivatives = self.number_of_derivatives
        self.F_derivatives = self.number_of_derivatives

        self.N_nu = sum(self.powerlist)

    @cached_property
    def U(self):
        # returns U with all Feynman parameters of inverse propagators set to zero
        U = self.preliminary_U
        for i in range(self.P-1,-1,-1):
            if self.powerlist[i].is_integer and self.powerlist[i].is_nonpositive:
                U = U.replace(i,0,remove=True).simplify()
        return U

    @cached_property
    def F(self):
        # returns F with all Feynman parameters of inverse propagators set to zero
        F = self.preliminary_F
        for i in range(self.P-1,-1,-1):
            if self.powerlist[i].is_integer and self.powerlist[i].is_nonpositive:
                F = F.replace(i,0,remove=True).simplify()
        return F

    @cached_property
    def numerator(self):

        Feynman_parameters_F_U = self.Feynman_parameters + sp.sympify(['F', 'U'])

        extended_expolist = []
        for exponents in self.preliminary_U.expolist:
            extended_expolist.append(np.concatenate([exponents,[0,0]]))

        U_explicit = Polynomial(extended_expolist, self.preliminary_U.coeffs, polysymbols=Feynman_parameters_F_U)

        extended_expolist = []
        for exponents in self.preliminary_F.expolist:
            extended_expolist.append(np.concatenate([exponents,[0,0]]))

        F_explicit = Polynomial(extended_expolist, self.preliminary_F.coeffs, polysymbols=Feynman_parameters_F_U)

        Nu = self.preliminary_numerator
        U = Polynomial.from_expression('U', Feynman_parameters_F_U)
        F = Polynomial.from_expression('F', Feynman_parameters_F_U)

        n = self.N_nu - self.dimensionality / 2 * (self.L + 1) - self.highest_rank
        m = self.N_nu - self.dimensionality / 2 * self.L

        # Loop backwards over Feynman parameters so that removing one parameter does not change the indexing
        # of the ones still to come.
        for i in range(self.P-1,-1,-1):

            # calculate k-fold derivative of U^n/F^m*Nu with respect to Feynman_parameters[i]
            # keeping F and U symbolic but calculating their derivatives explicitly
            # In each step factor out U^(n-1)/F^(m+1) or U^n/F^(m+1).
            k = self.derivativelist[i]

            if k != 0:
                dFdx = F_explicit.derive(i)
                dUdx = U_explicit.derive(i)
                for _ in range(k):
                    # The derivative of U^n/F^m*Nu is given by the sum of three terms:
                    # term1 = n * U^(n-1)/F^m * dU/dx * Nu
                    # term2 = -m * U^n/F^(m+1) * dF/dx * Nu
                    # term3 = U^n/F^m * ( dNu/dx + dNu/dF * dF/dx + dNu/dU * dU/dx )

                    # terms with all factors of U and F stripped off:
                    term1 = n*dUdx*Nu
                    term2 = - m*dFdx*Nu
                    term3 = Nu.derive(i) + Nu.derive(-2)*dFdx + Nu.derive(-1)*dUdx

                    # If term1 vanishes, we can factor out U^n.
                    if dUdx.coeffs.any() != 0:
                        # -> term1 non-zero -> factor out U^(n-1) rather than U^n
                        n -= 1
                        term2 *= U
                        term3 *= U

                    # dFdx will in practice never be the zero polynomial
                    # -> term2 always present -> factor out F^-(m+1) rather than F^-m
                    m += 1
                    term1 *= F
                    term3 *= F

                    Nu = term1 + term2 + term3

            # The k-fold derivative effectively increments the power of the propagator by k.
            # If the new 'effective power' is exactly zero, the corresponding parameter has to be set to zero.
            # Note that in the case where the power is zero from the start, this applies as well.
            newpower = self.powerlist[i] + k
            if newpower == 0:
                F_explicit = F_explicit.replace(i,0,remove=True).simplify()
                U_explicit = U_explicit.replace(i,0,remove=True).simplify()
                F = F.replace(i,0,remove=True).simplify()
                U = U.replace(i,0,remove=True).simplify()
                Nu = Nu.replace(i,0,remove=True).simplify()

        return Nu * (-1)**( self.N_nu + self.number_of_derivatives )

    @cached_property
    def measure(self):
        # The monomials x_i^(nu_i-1) multiplying the integration measure.
        # The factors of 1/Gamma(nu_i) are implemented in `Gamma_factor` together with the global Gamma.
        # TODO: define as Product of exponentiated monomials
        measure = 1

        Feynman_parameters_F_U = self.Feynman_parameters + sp.sympify(['F', 'U'])

        # The effective power to be used in the measure has to be increased by the number of derivatives.
        for i in range(self.P):
            eff_power = self.powerlist[i] + self.derivativelist[i]
            if eff_power != 0:
                expolist = np.zeros([1,len(Feynman_parameters_F_U)], dtype=int)
                expolist[0][i] = 1
                measure *= ExponentiatedPolynomial(expolist, np.array([1]), exponent = (eff_power - 1),
                                                   polysymbols = Feynman_parameters_F_U, copy=False)

        return measure.simplify()

    @cached_property
    def Gamma_argument(self):
        return self.N_nu - self.dimensionality * self.L/2 - self.highest_rank//2

    @cached_property
    def Gamma_factor(self):
        # Every term factor in the sum of equation (2.5) in arXiv:1010.1667v1 comes with
        # the scalar factor `1/(-2)**(r/2)*Gamma(N_nu - dim*L/2 - r/2)*F**(r/2)`.
        # In order to keep the `numerator` free of poles in the regulator, we divide it
        # by the Gamma function with the smallest argument `N_nu - dim*L/2 - highest_rank//2`,
        # where `//` means integer division, and put it here.
        gamma_fac = sp.gamma(self.Gamma_argument)

        # Multiply by the 1/Gamma(nu_i) factors belonging to the integration measure.
        # The effective power to be used in the gamma functions has to be increased by the number of derivatives.
        for i in range(self.P):
            eff_power = self.powerlist[i] + self.derivativelist[i]
            if eff_power != 0 :
                gamma_fac *= 1/sp.gamma(eff_power)

        return gamma_fac

    @cached_property
    def integration_variables(self):
        variables = []
        for FP,power in zip(self.Feynman_parameters, self.powerlist):
            if not (power.is_integer and power.is_nonpositive):
                variables.append(FP)
        return variables
