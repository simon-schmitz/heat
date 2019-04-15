import numpy as np
import torch

from . import arithmetics
from . import devices
from . import exponential
from . import io
from . import linalg
from . import logical
from . import memory
from . import relational
from . import rounding
from . import statistics
from . import trigonometrics
from . import types

from .stride_tricks import sanitize_axis


__all__ = [
    'Tensor'
]


class Tensor:
    def __init__(self, array, gshape, dtype, split, device, comm):
        self.__array = array
        self.__gshape = gshape
        self.__dtype = dtype
        self.__split = split
        self.__device = device
        self.__comm = comm

    @property
    def comm(self):
        return self.__comm

    @property
    def device(self):
        return self.__device

    @property
    def dtype(self):
        return self.__dtype

    @property
    def gshape(self):
        return self.__gshape

    @property
    def lshape(self):
        return tuple(self.__array.shape)

    @property
    def shape(self):
        return self.__gshape

    @property
    def split(self):
        return self.__split

    @property
    def T(self, axes=None):
        return linalg.transpose(self, axes)

    def abs(self, out=None, dtype=None):
        """
        Calculate the absolute value element-wise.

        Parameters
        ----------
        out : ht.Tensor, optional
            A location into which the result is stored. If provided, it must have a shape that the inputs broadcast to.
            If not provided or None, a freshly-allocated array is returned.
        dtype : ht.type, optional
            Determines the data type of the output array. The values are cast to this type with potential loss of
            precision.

        Returns
        -------
        absolute_values : ht.Tensor
            A tensor containing the absolute value of each element in x.
        """
        return rounding.abs(self, out, dtype)

    def absolute(self, out=None, dtype=None):
        """
        Calculate the absolute value element-wise.

        ht.abs is a shorthand for this function.

        Parameters
        ----------
        out : ht.Tensor, optional
            A location into which the result is stored. If provided, it must have a shape that the inputs broadcast to.
            If not provided or None, a freshly-allocated array is returned.
        dtype : ht.type, optional
            Determines the data type of the output array. The values are cast to this type with potential loss of
            precision.

        Returns
        -------
        absolute_values : ht.Tensor
            A tensor containing the absolute value of each element in x.

        """
        return self.abs(out, dtype)

    def __add__(self, other):
        """
        Element-wise addition of another tensor or a scalar to the tensor.
        Takes the second operand (scalar or tensor) whose elements are to be added as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to be added element-wise to the tensor

        Returns
        -------
        result: ht.Tensor
            A tensor containing the results of element-wise addition.

        Examples:
        ---------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2], [3, 4]])
        >>> T1.__add__(2.0)
        tensor([[3., 4.],
               [5., 6.]])

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__add__(T2)
        tensor([[3., 4.],
                [5., 6.]])
        """
        return arithmetics.add(self, other)

    def all(self, axis=None, out=None, keepdim=None):
        """
        Test whether all array elements along a given axis evaluate to True.

        Parameters:
        -----------
        axis : None or int or tuple of ints, optional
            Axis or axes along which a logical AND reduction is performed. The default (axis = None) is to perform a
            logical AND over all the dimensions of the input array. axis may be negative, in which case it counts
            from the last to the first axis.
        out : ht.Tensor, optional
            Alternate output array in which to place the result. It must have the same shape as the expected output
            and its type is preserved.

        Returns:
        --------
        all : ht.Tensor, bool
            A new boolean or ht.Tensor is returned unless out is specified, in which case a reference to out is returned.

        Examples:
        ---------
        >>> import heat as ht
        >>> a = ht.random.randn(4,5)
        >>> a
        tensor([[ 0.5370, -0.4117, -3.1062,  0.4897, -0.3231],
                [-0.5005, -1.7746,  0.8515, -0.9494, -0.2238],
                [-0.0444,  0.3388,  0.6805, -1.3856,  0.5422],
                [ 0.3184,  0.0185,  0.5256, -1.1653, -0.1665]])
        >>> x = a < 0.5
        >>> x
        tensor([[0, 1, 1, 1, 1],
                [1, 1, 0, 1, 1],
                [1, 1, 0, 1, 0],
                [1,1, 0, 1, 1]], dtype=torch.uint8)
        >>> x.all()
        tensor([0], dtype=torch.uint8)
        >>> x.all(axis=0)
        tensor([[0, 1, 0, 1, 0]], dtype=torch.uint8)
        >>> x.all(axis=1)
        tensor([[0],
                [0],
                [0],
                [0]], dtype=torch.uint8)

        Write out to predefined buffer:
        >>> out = ht.zeros((1,5))
        >>> x.all(axis=0, out=out)
        >>> out
        tensor([[0, 1, 0, 1, 0]], dtype=torch.uint8)
        """
        return logical.all(self, axis=axis, out=out, keepdim=keepdim)

    def allclose(self, other, rtol=1e-05, atol=1e-08, equal_nan=False):
        """
        Test whether self and other are element-wise equal within a tolerance. Returns True if |self - other| <= atol +
        rtol * |other| for all elements, False otherwise.

        Parameters:
        -----------
        other : ht.Tensor
            Input tensor to compare to

        atol: float, optional
            Absolute tolerance. Default is 1e-08

        rtol: float, optional
            Relative tolerance (with respect to y). Default is 1e-05

        equal_nan: bool, optional
            Whether to compare NaN’s as equal. If True, NaN’s in a will be considered equal to NaN’s in b in the output array.

        Returns:
        --------
        allclose : bool
            True if the two tensors are equal within the given tolerance; False otherwise.

        Examples:
        ---------
        >>> a = ht.float32([[2, 2], [2, 2]])
        >>> a.allclose(a)
        True

        >>> b = ht.float32([[2.00005,2.00005],[2.00005,2.00005]])
        >>> a.allclose(b)
        False
        >>> a.allclose(b, atol=1e-04)
        True
        """
        return logical.allclose(self, other, rtol, atol, equal_nan)

    def any(self, axis=None, out=None):
        """
        Test whether any array element along a given axis evaluates to True.
        The returning tensor is one dimensional unless axis is not None.

        Parameters:
        -----------
        axis : int, optional
            Axis along which a logic OR reduction is performed. With axis=None, the logical OR is performed over all
            dimensions of the tensor.
        out : tensor, optional
            Alternative output tensor in which to place the result. It must have the same shape as the expected output.
            The output is a tensor with dtype=bool.

        Returns:
        --------
        boolean_tensor : tensor of type bool
            Returns a tensor of booleans that are 1, if any non-zero values exist on this axis, 0 otherwise.

        Examples:
        ---------
        >>> import heat as ht
        >>> t = ht.float32([[0.3, 0, 0.5]])
        >>> t.any()
        tensor([1], dtype=torch.uint8)
        >>> t.any(axis=0)
        tensor([[1, 0, 1]], dtype=torch.uint8)
        >>> t.any(axis=1)
        tensor([[1]], dtype=torch.uint8)

        >>> t = ht.int32([[0, 0, 1], [0, 0, 0]])
        >>> res = ht.zeros((1, 3), dtype=ht.bool)
        >>> t.any(axis=0, out=res)
        tensor([[0, 0, 1]], dtype=torch.uint8)
        >>> res
        tensor([[0, 0, 1]], dtype=torch.uint8)
        """
        return logical.any(self, axis=axis, out=out)

    def argmax(self, axis=None, out=None, **kwargs):
        """
        Returns the indices of the maximum values along an axis.

        Parameters:	
        ----------
        x : ht.Tensor
            Input array.
        axis : int, optional
            By default, the index is into the flattened tensor, otherwise along the specified axis.
        out : array, optional
            If provided, the result will be inserted into this tensor. It should be of the appropriate shape and dtype.

        Returns:
        -------	
        index_tensor : ht.Tensor of ints
            Array of indices into the array. It has the same shape as x.shape with the dimension along axis removed.

        Examples:
        --------
        >>> import heat as ht
        >>> import torch
        >>> torch.manual_seed(1)
        >>> a = ht.random.randn(3,3)
        >>> a
        tensor([[-0.5631, -0.8923, -0.0583],
        [-0.1955, -0.9656,  0.4224],
        [ 0.2673, -0.4212, -0.5107]])
        >>> a.argmax()
        tensor([5])
        >>> a.argmax(axis=0)
        tensor([[2, 2, 1]])
        >>> a.argmax(axis=1)
        tensor([[2],
        [2],
        [0]])
        """
        return statistics.argmax(self, axis=axis, out=out, **kwargs)

    def argmin(self, axis=None, out=None, **kwargs):
        """
        Returns the indices of the minimum values along an axis.

        Parameters:	
        ----------
        x : ht.Tensor
            Input array.
        axis : int, optional
            By default, the index is into the flattened tensor, otherwise along the specified axis.
        out : array, optional
            If provided, the result will be inserted into this tensor. It should be of the appropriate shape and dtype.

        Returns:
        -------	
        index_tensor : ht.Tensor of ints
            Array of indices into the array. It has the same shape as x.shape with the dimension along axis removed.

        Examples
        --------
        >>> import heat as ht
        >>> import torch
        >>> torch.manual_seed(1)
        >>> a = ht.random.randn(3,3)
        >>> a
        tensor([[-0.5631, -0.8923, -0.0583],
        [-0.1955, -0.9656,  0.4224],
        [ 0.2673, -0.4212, -0.5107]])
        >>> a.argmin()
        tensor([4])
        >>> a.argmin(axis=0)
        tensor([[0, 1, 2]])
        >>> a.argmin(axis=1)
        tensor([[1],
                [1],
                [2]])
        """
        return statistics.argmin(self, axis=axis, out=out, **kwargs)

    def astype(self, dtype, copy=True):
        """
        Returns a casted version of this array.

        Parameters
        ----------
        dtype : ht.dtype
            HeAT type to which the array is cast
        copy : bool, optional
            By default the operation returns a copy of this array. If copy is set to false the cast is performed
            in-place and this tensor is returned

        Returns
        -------
        casted_tensor : ht.Tensor
            casted_tensor is a new tensor of the same shape but with given type of this tensor. If copy is True, the
            same tensor is returned instead.
        """
        dtype = types.canonical_heat_type(dtype)
        casted_array = self.__array.type(dtype.torch_type())
        if copy:
            return Tensor(casted_array, self.shape, dtype, self.split, self.device, self.comm)

        self.__array = casted_array
        self.__dtype = dtype

        return self

    def ceil(self, out=None):
        """
        Return the ceil of the input, element-wise.

        The ceil of the scalar x is the largest integer i, such that i <= x. It is often denoted as \lceil x \rceil.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        ceiled : ht.Tensor
            A tensor of the same shape as x, containing the ceiled valued of each element in this tensor. If out was
            provided, ceiled is a reference to it.

        Returns
        -------
        ceiled : ht.Tensor
            A tensor of the same shape as x, containing the floored valued of each element in this tensor. If out was
            provided, ceiled is a reference to it.

        Examples
        --------
        >>> ht.arange(-2.0, 2.0, 0.4).ceil()
        tensor([-2., -1., -1., -0., -0., -0.,  1.,  1.,  2.,  2.])
        """
        return rounding.ceil(self, out)

    def clip(self, a_min, a_max, out=None):
        """
        Parameters
        ----------
        a_min : scalar or None
            Minimum value. If None, clipping is not performed on lower interval edge. Not more than one of a_min and
            a_max may be None.
        a_max : scalar or None
            Maximum value. If None, clipping is not performed on upper interval edge. Not more than one of a_min and
            a_max may be None.
        out : ht.Tensor, optional
            The results will be placed in this array. It may be the input array for in-place clipping. out must be of
            the right shape to hold the output. Its type is preserved.

        Returns
        -------
        clipped_values : ht.Tensor
            A tensor with the elements of this tensor, but where values < a_min are replaced with a_min, and those >
            a_max with a_max.
        """
        return rounding.clip(self, a_min, a_max, out)

    def copy(self):
        """
        Return an array copy of the given object.

        Returns
        -------
        copied : ht.Tensor
            A copy of the original
        """
        return memory.copy(self)

    def cos(self, out=None):
        """
        Return the trigonometric cosine, element-wise.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        cosine : ht.Tensor
            A tensor of the same shape as x, containing the trigonometric cosine of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, square_roots is a reference to it.

        Examples
        --------
        >>> ht.arange(-6, 7, 2).cos()
        tensor([ 0.9602, -0.6536, -0.4161,  1.0000, -0.4161, -0.6536,  0.9602])
        """
        return trigonometrics.cos(self, out)

    def cosh(self, out=None):
        """
        Return the hyperbolic cosine, element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the hyperbolic cosine.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        hyperbolic cosine : ht.Tensor
            A tensor of the same shape as x, containing the hyperbolic cosine of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, square_roots is a reference to it.

        Examples
        --------
        >>> ht.cosh(ht.arange(-6, 7, 2))
        tensor([201.7156,  27.3082,   3.7622,   1.0000,   3.7622,  27.3082, 201.7156])
        """
        return trigonometrics.cosh(self, out)

    def cpu(self):
        """
        Returns a copy of this object in main memory. If this object is already in main memory, then no copy is
        performed and the original object is returned.

        Returns
        -------
        tensor_on_device : ht.Tensor
            A copy of this object on the CPU.
        """
        self.__array = self.__array.cpu()
        return self

    def __eq__(self, other):
        """
        Element-wise rich comparison of equality with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare equality

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values of self are equal to values of other, 0 for all other
            elements

        Examples:
        ---------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T1.__eq__(3.0)
        tensor([[0, 0],
                [1, 0]])

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__eq__(T2)
        tensor([[0, 1],
                [0, 0]])
        """

    def exp(self, out=None):
        """
        Calculate the exponential of all elements in the input array.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        exponentials : ht.Tensor
            A tensor of the same shape as x, containing the positive exponentials of each element in this tensor. If out
            was provided, logarithms is a reference to it.

        Examples
        --------
        >>> ht.arange(5).exp()
        tensor([ 1.0000,  2.7183,  7.3891, 20.0855, 54.5981])
        """
        return exponential.exp(self, out)

    def exp2(self, out=None):
        """
        Calculate the exponential of all elements in the input array.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        exponentials : ht.Tensor
            A tensor of the same shape as x, containing the positive exponentials of each element in this tensor. If out
            was provided, logarithms is a reference to it.

        Examples
        --------
        >>> ht.exp2(ht.arange(5))
        tensor([ 1.,  2.,  4.,  8., 16.], dtype=torch.float64)
        """
        return exponential.exp2(self, out)

    def expand_dims(self, axis):
        # TODO: document me
        # TODO: test me
        # TODO: sanitize input
        # TODO: make me more numpy API complete
        # TODO: fix negative axis
        return Tensor(
            self.__array.unsqueeze(dim=axis),
            self.shape[:axis] + (1,) + self.shape[axis:],
            self.dtype,
            self.split if self.split is None or self.split < axis else self.split + 1,
            self.device,
            self.comm
        )

    def floor(self, out=None):
        """
        Return the floor of the input, element-wise.

        The floor of the scalar x is the largest integer i, such that i <= x. It is often denoted as :math:`\lfloor x
        \rfloor`.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        floored : ht.Tensor
            A tensor of the same shape as x, containing the floored valued of each element in this tensor. If out was
            provided, floored is a reference to it.

        Examples
        --------
        >>> ht.floor(ht.arange(-2.0, 2.0, 0.4))
        tensor([-2., -2., -2., -1., -1.,  0.,  0.,  0.,  1.,  1.])
        """
        return rounding.floor(self, out)

    def __ge__(self, other):
        """
        Element-wise rich comparison of relation "greater than or equal" with values from second operand (scalar or
        tensor).
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare elements from tensor

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values in self are greater than or equal to values of other
            (x1 >= x2), 0 for all other elements

        Examples
        -------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T1.__ge__(3.0)
        tensor([[0, 0],
                [1, 1]], dtype=torch.uint8)
        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__ge__(T2)
        tensor([[0, 1],
                [1, 1]], dtype=torch.uint8)
        """
        return relational.ge(self, other)

    def __getitem__(self, key):
        # TODO: document me
        # TODO: test me
        # TODO: sanitize input
        # TODO: make me more numpy API complete
        return Tensor(self.__array[key], self.shape, self.split, self.device, self.comm)

    if torch.cuda.device_count() > 0:
        def gpu(self):
            """
            Returns a copy of this object in GPU memory. If this object is already in GPU memory, then no copy is
            performed and the original object is returned.

            Returns
            -------
            tensor_on_device : ht.Tensor
                A copy of this object on the GPU.
            """
            self.__array = self.__array.cuda(devices.gpu_index())
            return self

    def __gt__(self, other):
        """
        Element-wise rich comparison of relation "greater than" with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare elements from tensor

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values in self are greater than values of other (x1 > x2),
            0 for all other elements

         Examples
         -------
         >>> import heat as ht
         >>> T1 = ht.float32([[1, 2],[3, 4]])
         >>> T1.__gt__(3.0)
         tensor([[0, 0],
                 [0, 1]], dtype=torch.uint8)

         >>> T2 = ht.float32([[2, 2], [2, 2]])
         >>> T1.__gt__(T2)
         tensor([[0, 0],
                 [1, 1]], dtype=torch.uint8)

        """
        return relational.gt(self, other)

    def is_distributed(self):
        """
        Determines whether the data of this tensor is distributed across multiple processes.

        Returns
        -------
        is_distributed : bool
            Whether the data of the tensor is distributed across multiple processes
        """
        return self.split is not None and self.comm.is_distributed()

    def __le__(self, other):
        """
        Element-wise rich comparison of relation "less than or equal" with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare elements from tensor

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values in self are less than or equal to values of other (x1 <= x2),
            0 for all other elements

        Examples
        -------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T1.__le__(3.0)
        tensor([[1, 1],
                [1, 0]], dtype=torch.uint8)

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__le__(T2)
        tensor([[1, 1],
                [0, 0]], dtype=torch.uint8)

        """
        return relational.le(self, other)

    def log(self, out=None):
        """
        Natural logarithm, element-wise.

        The natural logarithm log is the inverse of the exponential function, so that log(exp(x)) = x. The natural
        logarithm is logarithm in base e.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        logarithms : ht.Tensor
            A tensor of the same shape as x, containing the positive logarithms of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, logarithms is a reference to it.

        Examples
        --------
        >>> ht.arange(5).log()
        tensor([  -inf, 0.0000, 0.6931, 1.0986, 1.3863])
        """
        return exponential.log(self, out)

    def log2(self, out=None):
        """
        log base 2, element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the logarithm.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        logarithms : ht.Tensor
            A tensor of the same shape as x, containing the positive logarithms of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, logarithms is a reference to it.

        Examples
        --------
        >>> ht.log2(ht.arange(5))
        tensor([  -inf, 0.0000, 1.0000, 1.5850, 2.0000])
        """
        return exponential.log2(self, out)

    def log10(self, out=None):
        """
        log base 10, element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the logarithm.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        logarithms : ht.Tensor
            A tensor of the same shape as x, containing the positive logarithms of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, logarithms is a reference to it.

        Examples
        --------
        >>> ht.log10(ht.arange(5))
        tensor([-inf, 0.0000, 1.0000, 1.5850, 2.0000])
        """
        return exponential.log10(self, out)

    def __lt__(self, other):
        """
        Element-wise rich comparison of relation "less than" with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare elements from tensor

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values in self are less than values of other (x1 < x2),
            0 for all other elements

        Examples
        -------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T1.__lt__(3.0)
        tensor([[1, 1],
               [0, 0]], dtype=torch.uint8)

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__lt__(T2)
        tensor([[1, 0],
               [0, 0]], dtype=torch.uint8)

        """
        return relational.lt(self, other)

    def max(self, axis=None, out=None, keepdim=None):
        """
        Return the maximum of an array or maximum along an axis.

        Parameters
        ----------
        self : ht.Tensor
            Input data.

        axis : None or int  
            Axis or axes along which to operate. By default, flattened input is used.
        #TODO: out : ht.Tensor, optional
            Alternative output array in which to place the result. Must be of the same shape and buffer length as the
            expected output.
        #TODO: initial : scalar, optional   
            The minimum value of an output element. Must be present to allow computation on empty slice.
        """
        return statistics.max(self, axis=axis, out=out, keepdim=keepdim)

    def mean(self, axis):
        # TODO: document me
        # TODO: test me
        # TODO: sanitize input
        # TODO: make me more numpy API complete
        return self.sum(axis) / self.shape[axis]

    def min(self, axis=None, out=None, keepdim=None):
        """
        Return the minimum of an array or minimum along an axis.

        Parameters
        ----------
        self : ht.Tensor
            Input data.
        axis : None or int
            Axis or axes along which to operate. By default, flattened input is used.
        #TODO: out : ht.Tensor, optional
            Alternative output array in which to place the result. Must be of the same shape and buffer length as the
            expected output.
        #TODO: initial : scalar, optional   
            The maximum value of an output element. Must be present to allow computation on empty slice.
        """
        return statistics.min(self, axis=axis, out=out, keepdim=keepdim)

    def __mod__(self, other):
        """
            Element-wise division remainder of values of self by values of operand other (i.e. self % other), not commutative.
            Takes the two operands (scalar or tensor) whose elements are to be divided (operand 1 by operand 2)
            as arguments.

            Parameters
            ----------
            other: tensor or scalar
                The second operand by whose values it self to be divided.

            Returns
            -------
            result: ht.Tensor
                A tensor containing the remainder of the element-wise division of self by other.

            Examples:
            ---------
            >>> import heat as ht
            >>> ht.mod(2, 2)
            tensor([0])

            >>> T1 = ht.int32([[1, 2], [3, 4]])
            >>> T2 = ht.int32([[2, 2], [2, 2]])
            >>> T1 % T2
            tensor([[1, 0],
                    [1, 0]], dtype=torch.int32)

            >>> s = ht.int32([2])
            >>> s % T1
            tensor([[0, 0]
                    [2, 2]], dtype=torch.int32)
            """
        return arithmetics.mod(self, other)

    def __mul__(self, other):
        """
        Element-wise multiplication (not matrix multiplication) with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) whose values to multiply to the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
           The value(s) to multiply to the tensor (element-wise)

        Returns
        -------
        result: ht.Tensor
           A tensor containing the results of element-wise multiplication.

        Examples:
        ---------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2], [3, 4]])
        >>> T1.__mul__(3.0)
        tensor([[3., 6.],
            [9., 12.]])

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__mul__(T2)
        tensor([[2., 4.],
            [6., 8.]])
        """
        return arithmetics.mul(self, other)

    def __ne__(self, other):
        """
        Element-wise rich comparison of non-equality with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) to which to compare the first tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to which to compare equality

        Returns
        -------
        result: ht.Tensor
            Tensor holding 1 for all elements in which values of self are equal to values of other,
            0 for all other elements

        Examples:
        ---------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T1.__ne__(3.0)
        tensor([[1, 1],
                [0, 1]])

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__ne__(T2)
        tensor([[1, 0],
                [1, 1]])
        """
        return relational.ne(self, other)

    def __pow__(self, other):
        """
        Element-wise exponential function with values from second operand (scalar or tensor)
        Takes the second operand (scalar or tensor) whose values are the exponent to be applied to the first
        tensor as argument.

        Parameters
        ----------
        other: tensor or scalar
           The value(s) in the exponent (element-wise)

        Returns
        -------
        result: ht.Tensor
           A tensor containing the results of element-wise exponential operation.

        Examples:
        ---------
        >>> import heat as ht

        >>> T1 = ht.float32([[1, 2], [3, 4]])
        >>> T1.__pow__(3.0)
        tensor([[1., 8.],
                [27., 64.]])

        >>> T2 = ht.float32([[3, 3], [2, 2]])
        >>> T1.__pow__(T2)
        tensor([[1., 8.],
                [9., 16.]])
        """
        return arithmetics.pow(self, other)

    def __repr__(self, *args):
        # TODO: document me
        # TODO: generate none-PyTorch repr
        return self.__array.__repr__(*args)

    def resplit(self, axis=None):
        """
        In-place redistribution of the content of the tensor. Allows to "unsplit" (i.e. gather) all values from all
        nodes as well as the definition of new axis along which the tensor is split without changes to the values.

        WARNING: this operation might involve a significant communication overhead. Use it sparingly and preferably for
        small tensors.

        Parameters
        ----------
        axis : int
            The new split axis, None denotes gathering, an int will set the new split axis

        Returns
        -------
        resplit: ht.Tensor
            The redistributed tensor

        Examples
        --------
        a = ht.zeros((4, 5,), split=0)
        a.lshape
        (0/2) >>> (2, 5)
        (1/2) >>> (2, 5)
        a.resplit(None)
        a.split
        >>> None
        a.lshape
        (0/2) >>> (4, 5)
        (1/2) >>> (4, 5)

        a = ht.zeros((4, 5,), split=0)
        a.lshape
        (0/2) >>> (2, 5)
        (1/2) >>> (2, 5)
        a.resplit(1)
        a.split
        >>> 1
        a.lshape
        (0/2) >>> (4, 3)
        (1/2) >>> (4, 2)
        """
        # sanitize the axis to check whether it is in range
        axis = sanitize_axis(self.shape, axis)

        # early out for unchanged content
        if axis == self.split:
            return self

        # unsplit the tensor
        if axis is None:
            gathered = torch.empty(self.shape)

            recv_counts, recv_displs, _ = self.comm.counts_displs_shape(self.shape, self.split)
            self.comm.Allgatherv(self.__array, (gathered, recv_counts, recv_displs,), recv_axis=axis)

            self.__array = gathered
            self.__split = None

        # tensor needs be split/sliced locally
        elif self.split is None:
            _, _, slices = self.comm.chunk(self.shape, axis)
            self.__array = self.__array[slices]
            self.__split = axis

        # entirely new split axis, need to redistribute
        else:
            _, output_shape, _ = self.comm.chunk(self.shape, axis)
            redistributed = torch.empty(output_shape)

            send_counts, send_displs, _ = self.comm.counts_displs_shape(self.lshape, axis)
            recv_counts, recv_displs, _ = self.comm.counts_displs_shape(self.shape, self.split)

            self.comm.Alltoallv(
                (self.__array, send_counts, send_displs,),
                (redistributed, recv_counts, recv_displs,),
                axis=axis, recv_axis=self.split
            )

            self.__array = redistributed
            self.__split = axis

        return self

    def save(self, path, *args, **kwargs):
        """
        Save the tensor's data to disk. Attempts to auto-detect the file format by determining the extension.

        Parameters
        ----------
        self : ht.Tensor
            The tensor holding the data to be stored
        path : str
            Path to the file to be stored.
        args/kwargs : list/dict
            additional options passed to the particular functions.

        Raises
        -------
        ValueError
            If the file extension is not understood or known.

        Examples
        --------
        >>> a = ht.arange(100, split=0)
        >>> a.save('data.h5', 'DATA', mode='a')
        >>> a.save('data.nc', 'DATA', mode='w')
        """
        return io.save(self, path, *args, **kwargs)

    if io.supports_hdf5():
        def save_hdf5(self, path, dataset, mode='w', **kwargs):
            """
            Saves data to an HDF5 file. Attempts to utilize parallel I/O if possible.

            Parameters
            ----------
            path : str
                Path to the HDF5 file to be written.
            dataset : str
                Name of the dataset the data is saved to.
            mode : str, one of 'w', 'a', 'r+'
                File access mode
            kwargs : dict
                additional arguments passed to the created dataset.

            Raises
            -------
            TypeError
                If any of the input parameters are not of correct type.
            ValueError
                If the access mode is not understood.

            Examples
            --------
            >>> ht.arange(100, split=0).save_hdf5('data.h5', dataset='DATA')
            """
            return io.save_hdf5(self, path, dataset, mode, **kwargs)

    if io.supports_netcdf():
        def save_netcdf(self, path, variable, mode='w', **kwargs):
            """
            Saves data to a netCDF4 file. Attempts to utilize parallel I/O if possible.

            Parameters
            ----------
            path : str
                Path to the netCDF4 file to be written.
            variable : str
                Name of the variable the data is saved to.
            mode : str, one of 'w', 'a', 'r+'
                File access mode
            kwargs : dict
                additional arguments passed to the created dataset.

            Raises
            -------
            TypeError
                If any of the input parameters are not of correct type.
            ValueError
                If the access mode is not understood.

            Examples
            --------
            >>> ht.arange(100, split=0).save_netcdf('data.nc', dataset='DATA')
            """
            return io.save_netcdf(self, path, variable, mode, **kwargs)

    def __setitem__(self, key, value):
        # TODO: document me
        # TODO: test me
        # TODO: sanitize input
        # TODO: make me more numpy API complete
        if self.__split is not None:
            raise NotImplementedError('Slicing not supported for __split != None')

        if np.isscalar(value):
            self.__array.__setitem__(key, value)
        elif isinstance(value, Tensor):
            self.__array.__setitem__(key, value.__array)
        else:
            raise NotImplementedError('Not implemented for {}'.format(value.__class__.__name__))

    def sin(self, out=None):
        """
        Return the trigonometric sine, element-wise.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        sine : ht.Tensor
            A tensor of the same shape as x, containing the trigonometric sine of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, square_roots is a reference to it.

        Examples
        --------
        >>> ht.arange(-6, 7, 2).sin()
        tensor([ 0.2794,  0.7568, -0.9093,  0.0000,  0.9093, -0.7568, -0.2794])
        """
        return trigonometrics.sin(self, out)

    def sinh(self, out=None):
        """
        Return the hyperbolic sine, element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the hyperbolic sine.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        hyperbolic sine : ht.Tensor
            A tensor of the same shape as x, containing the trigonometric sine of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, square_roots is a reference to it.

        Examples
        --------
        >>> ht.sinh(ht.arange(-6, 7, 2))
        tensor([[-201.7132,  -27.2899,   -3.6269,    0.0000,    3.6269,   27.2899,  201.7132])
        """
        return trigonometrics.sinh(self, out)

    def sqrt(self, out=None):
        """
        Return the non-negative square-root of the tensor element-wise.

        Parameters
        ----------
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        square_roots : ht.Tensor
            A tensor of the same shape as x, containing the positive square-root of each element in this tensor.
            Negative input elements are returned as nan. If out was provided, square_roots is a reference to it.

        Examples
        --------
        >>> ht.arange(5).sqrt()
        tensor([0.0000, 1.0000, 1.4142, 1.7321, 2.0000])
        >>> ht.arange(-5, 0).sqrt()
        tensor([nan, nan, nan, nan, nan])
        """
        return exponential.sqrt(self, out)

    def __str__(self, *args):
        # TODO: document me
        # TODO: generate none-PyTorch str
        return self.__array.__str__(*args)

    def __sub__(self, other):
        """
        Element-wise subtraction of another tensor or a scalar from the tensor.
        Takes the second operand (scalar or tensor) whose elements are to be subtracted  as argument.

        Parameters
        ----------
        other: tensor or scalar
            The value(s) to be subtracted element-wise from the tensor

        Returns
        -------
        result: ht.Tensor
            A tensor containing the results of element-wise subtraction.

        Examples:
        ---------
        >>> import heat as ht
        >>> T1 = ht.float32([[1, 2], [3, 4]])
        >>> T1.__sub__(2.0)
        tensor([[ 1.,  0.],
                [-1., -2.]])

        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__sub__(T2)
        tensor([[-1., 0.],
                [1., 2.]])
        """
        return arithmetics.sub(self, other)

    def sum(self, axis=None, out=None, keepdim=None):
        """
        Sum of array elements over a given axis.

        Parameters
        ----------
        axis : None or int or tuple of ints, optional
            Axis along which a sum is performed. The default, axis=None, will sum
            all of the elements of the input array. If axis is negative it counts
            from the last to the first axis.

            If axis is a tuple of ints, a sum is performed on all of the axes specified 
            in the tuple instead of a single axis or all the axes as before.

         Returns
         -------
         sum_along_axis : ht.Tensor
             An array with the same shape as self.__array except for the specified axis which
             becomes one, e.g. a.shape = (1,2,3) => ht.ones((1,2,3)).sum(axis=1).shape = (1,1,3)

        Examples
        --------
        >>> ht.ones(2).sum()
        tensor([2.])

        >>> ht.ones((3,3)).sum()
        tensor([9.])

        >>> ht.ones((3,3)).astype(ht.int).sum()
        tensor([9])

        >>> ht.ones((3,2,1)).sum(axis=-3)
        tensor([[[3.],
                 [3.]]])
        """
        return arithmetics.sum(self, axis=axis, out=out, keepdim=keepdim)

    def tan(self, out=None):
        """
        Compute tangent element-wise.

        Equivalent to ht.sin(x) / ht.cos(x) element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the trigonometric tangent.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        tangent : ht.Tensor
            A tensor of the same shape as x, containing the trigonometric tangent of each element in this tensor.

        Examples
        --------
        >>> ht.arange(-6, 7, 2).tan()
        tensor([ 0.29100619, -1.15782128,  2.18503986,  0., -2.18503986, 1.15782128, -0.29100619])
        """
        return trigonometrics.tan(self, out)

    def tanh(self, out=None):
        """
        Return the hyperbolic tangent, element-wise.

        Parameters
        ----------
        x : ht.Tensor
            The value for which to compute the hyperbolic tangent.
        out : ht.Tensor or None, optional
            A location in which to store the results. If provided, it must have a broadcastable shape. If not provided
            or set to None, a fresh tensor is allocated.

        Returns
        -------
        hyperbolic tangent : ht.Tensor
            A tensor of the same shape as x, containing the hyperbolic tangent of each element in this tensor.

        Examples
        --------
        >>> ht.tanh(ht.arange(-6, 7, 2))
        tensor([-1.0000, -0.9993, -0.9640,  0.0000,  0.9640,  0.9993,  1.0000])
        """
        return trigonometrics.tanh(self, out)

    def transpose(self, axes=None):
        """
        Permute the dimensions of an array.

        Parameters
        ----------
        axes : None or list of ints, optional
            By default, reverse the dimensions, otherwise permute the axes according to the values given.

        Returns
        -------
        p : ht.Tensor
            a with its axes permuted.

        Examples
        --------
        >>> a = ht.array([[1, 2], [3, 4]])
        >>> a
        tensor([[1, 2],
                [3, 4]])
        >>> a.transpose()
        tensor([[1, 3],
                [2, 4]])
        >>> a.transpose((1, 0))
        tensor([[1, 3],
                [2, 4]])
        >>> a.transpose(1, 0)
        tensor([[1, 3],
                [2, 4]])

        >>> x = ht.ones((1, 2, 3))
        >>> ht.transpose(x, (1, 0, 2)).shape
        (2, 1, 3)
        """
        return linalg.transpose(self, axes)

    def tril(self, k=0):
        """
        Returns the lower triangular part of the tensor, the other elements of the result tensor are set to 0.

        The lower triangular part of the tensor is defined as the elements on and below the diagonal.

        The argument k controls which diagonal to consider. If k=0, all elements on and below the main diagonal are
        retained. A positive value includes just as many diagonals above the main diagonal, and similarly a negative
        value excludes just as many diagonals below the main diagonal.

        Parameters
        ----------
        k : int, optional
            Diagonal above which to zero elements. k=0 (default) is the main diagonal, k<0 is below and k>0 is above.

        Returns
        -------
        lower_triangle : ht.Tensor
            Lower triangle of the input tensor.
        """
        return linalg.tril(self, k)

    def triu(self, k=0):
        """
        Returns the upper triangular part of the tensor, the other elements of the result tensor are set to 0.

        The upper triangular part of the tensor is defined as the elements on and below the diagonal.

        The argument k controls which diagonal to consider. If k=0, all elements on and below the main diagonal are
        retained. A positive value includes just as many diagonals above the main diagonal, and similarly a negative
        value excludes just as many diagonals below the main diagonal.

        Parameters
        ----------
        k : int, optional
            Diagonal above which to zero elements. k=0 (default) is the main diagonal, k<0 is below and k>0 is above.

        Returns
        -------
        upper_triangle : ht.Tensor
            Upper triangle of the input tensor.
        """
        return linalg.triu(self, k)

    def __truediv__(self, other):
        """
        Element-wise true division (i.e. result is floating point value rather than rounded int (floor))
        of the tensor by another tensor or scalar. Takes the second operand (scalar or tensor) by which to divide
        as argument.

        Parameters
        ----------
        other: tensor or scalar
           The value(s) by which to divide the tensor (element-wise)

        Returns
        -------
        result: ht.Tensor
           A tensor containing the results of element-wise division.

        Examples:
        ---------
        >>> import heat as ht
        >>> ht.div(2.0, 2.0)
        tensor([1.])

        >>> T1 = ht.float32([[1, 2],[3, 4]])
        >>> T2 = ht.float32([[2, 2], [2, 2]])
        >>> T1.__div__(T2)
        tensor([[0.5000, 1.0000],
                [1.5000, 2.0000]])

        >>> s = 2.0
        >>> T1.__div__(s)
        tensor([[0.5000, 1.0000],
                [1.5, 2.0000]])
        """
        return arithmetics.div(self, other)