import os, pdb, platform, time, warnings
import ctypes as ct
import numpy as np
import scipy.sparse as sp

MAX_ONES = 1024*1024*32

if platform.system() == 'Windows':
    _cudamat = ct.cdll.LoadLibrary('libcudamat.dll')
else:
    _cudamat = ct.cdll.LoadLibrary(f'{os.getcwd()}/cudamat/libcudamat.so')

_cudamat.get_last_cuda_error.restype = ct.c_char_p
_cudamat.cublas_init.restype = ct.c_int
_cudamat.cublas_shutdown.restype = ct.c_int
_cudamat.cuda_set_device.restype = ct.c_int
_cudamat.init_random.restype = ct.c_int

_cudamat.init_empty.restype = ct.c_int
_cudamat.reshape.restype = ct.c_int
_cudamat.copy_to_host.restype = ct.c_int
_cudamat.allocate_device_memory = ct.c_int
_cudamat.copy_to_device.restype = ct.c_int
_cudamat.copy_on_device.restype = ct.c_int
_cudamat.free_device_memory.restype = ct.c_int

_cudamat.get_slice.restype = ct.c_int
_cudamat.get_row_slice.restype = ct.c_int
_cudamat.set_row_slice.restype = ct.c_int
_cudamat.copy_transpose.restype = ct.c_int
_cudamat.get_vector_slice.restype = ct.c_int
_cudamat.fill_with_rand.restype = ct.c_int
_cudamat.fill_with_randn.restype = ct.c_int

_cudamat.add_col_vec.restype = ct.c_int
_cudamat.add_col_mult.restype = ct.c_int
_cudamat.add_row_mult.restype = ct.c_int
_cudamat.add_row_vec.restype = ct.c_int
_cudamat.mult_by_col_vec.restype = ct.c_int
_cudamat.mult_by_row_vec.restype = ct.c_int

_cudamat.less_than.restype = ct.c_int
_cudamat.less_than_scalar.restype = ct.c_int
_cudamat.greater_than.restype = ct.c_int
_cudamat.greater_than_scalar.restype = ct.c_int
_cudamat.max_by_axis.restype = ct.c_int
_cudamat.argmax_by_axis.restype = ct.c_int
_cudamat.sqsum_by_axis.restype = ct.c_int
_cudamat.normlimit_by_axis.restype = ct.c_int
_cudamat.sign.restype = ct.c_int
_cudamat.apply_sigmoid.restype = ct.c_int
_cudamat.apply_tanh.restype = ct.c_int
_cudamat.apply_abs.restype = ct.c_int
_cudamat.apply_log_1_plus_exp.restype = ct.c_int
_cudamat.apply_log.restype = ct.c_int
_cudamat.apply_floor.restype = ct.c_int
_cudamat.apply_ceil.restype = ct.c_int
_cudamat.apply_exp.restype = ct.c_int
_cudamat.apply_sqrt.restype = ct.c_int
_cudamat.apply_pow.restype = ct.c_int
_cudamat.apply_pow_matrix.restype = ct.c_int
_cudamat.reciprocal.restype = ct.c_int

_cudamat.add_elementwise.restype = ct.c_int
_cudamat.subtract_elementwise.restype = ct.c_int
_cudamat.divide_elementwise.restype = ct.c_int
_cudamat.mult_elementwise.restype = ct.c_int
_cudamat.apply_logistic_deriv.restype = ct.c_int
_cudamat.assign_scalar.restype = ct.c_int
_cudamat.mult_by_scalar.restype = ct.c_int
_cudamat.divide_by_scalar.restype = ct.c_int
_cudamat.add_scalar.restype = ct.c_int

_cudamat.read_from.restype = ct.c_float
_cudamat.sum_all.restype = ct.c_float
_cudamat.euclid_norm.restype = ct.c_float
_cudamat.selectRows.restype = ct.c_int
_cudamat.setSelectedRows.restype = ct.c_int
_cudamat.vdot.restype = ct.c_float
_cudamat.dot.restype = ct.c_int

def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""

    def newFunc(*args, **kwargs):
        warnings.warn(
            f"Call to deprecated function {func.__name__}.",
            category=DeprecationWarning,
        )
        return func(*args, **kwargs)

    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc

class CUDAMatException(Exception):
    pass

def get_last_cuda_error():
    return str(_cudamat.get_last_cuda_error())

def generate_exception(err_code):
    """
    Return a CUDAMatException object based on the error code err_code.
    """

    if err_code == -1:
        return CUDAMatException("Incompatible matrix dimensions.")
    elif err_code == -2:
        return CUDAMatException("CUBLAS error.")
    elif err_code == -3:
        return CUDAMatException(f"CUDA error: {get_last_cuda_error()}")
    elif err_code == -4:
        return CUDAMatException("Operation not supported on views.")
    elif err_code == -5:
        return CUDAMatException("Operation not supported on transposed matrices.")
    elif err_code == -6:
        return CUDAMatException("")
    elif err_code == -7:
        return CUDAMatException("Incompatible transposedness.")
    elif err_code == -8:
        return CUDAMatException("Matrix is not in device memory.")
    elif err_code == -9:
        return CUDAMatException("Operation not supported.")
        

class cudamat(ct.Structure):
    _fields_ = [('data_host', ct.POINTER(ct.c_float)),
                ('data_device', ct.POINTER(ct.c_float)),
                ('on_device', ct.c_int),
                ('on_host', ct.c_int),
                ('size', ct.c_int * 2),
                ('is_trans', ct.c_int),
                ('owns_data', ct.c_int),
                ('tex_obj', ct.c_ulonglong)]

class ConvDesc(ct.Structure):
    _fields_ = [('num_input_channels', ct.c_int),
                ('num_output_channels', ct.c_int),
                ('kernel_size_y', ct.c_int),
                ('kernel_size_x', ct.c_int),
                ('kernel_size_t', ct.c_int),
                ('stride_y', ct.c_int),
                ('stride_x', ct.c_int),
                ('stride_t', ct.c_int),
                ('padding_y', ct.c_int),
                ('padding_x', ct.c_int),
                ('padding_t', ct.c_int),
                ('input_channel_begin', ct.c_int),
                ('input_channel_end', ct.c_int),
                ('output_channel_begin', ct.c_int),
                ('output_channel_end', ct.c_int),
                ('num_groups', ct.c_int),
               ]

class Shape4D(ct.Structure):
    _fields_ = [('shape', ct.c_int * 4)]

def GetConvDesc(num_input_channels, num_output_channels, kernel_size_y,
                kernel_size_x, stride_y, stride_x, padding_y, padding_x,
                kernel_size_t=1, stride_t=1, padding_t=0,
                input_channel_begin=0, input_channel_end=0,
                output_channel_begin=0, output_channel_end=0,
                num_groups=1):
  if input_channel_end == 0:
    input_channel_end = num_input_channels
  if output_channel_end == 0:
    output_channel_end = num_output_channels
  return ConvDesc(num_input_channels, num_output_channels, kernel_size_y,
                  kernel_size_x, kernel_size_t, stride_y, stride_x, stride_t,
                  -padding_y, -padding_x, -padding_t,
                  input_channel_begin, input_channel_end,
                  output_channel_begin, output_channel_end,
                  num_groups)

def GetConvDescTuple(cd):
  return (
    cd.num_output_channels,
    cd.kernel_size_y,
    cd.kernel_size_x,
    cd.stride_y,
    cd.stride_x,
    -cd.padding_y,
    -cd.padding_x,
         )

def GetConvDescTuple3D(cd):
  return (
    cd.num_output_channels,
    cd.kernel_size_y,
    cd.kernel_size_x,
    cd.kernel_size_t,
    cd.stride_y,
    cd.stride_x,
    cd.stride_t,
    -cd.padding_y,
    -cd.padding_x,
    -cd.padding_t,
         )

def GetInputSize(cd):
  return (cd.input_channel_end - cd.input_channel_begin) * cd.kernel_size_x * cd.kernel_size_y * cd.kernel_size_t

def GetOutputSize(cd):
  return cd.output_channel_end - cd.output_channel_begin

def GetWShape(cd):
  return (cd.output_channel_end - cd.output_channel_begin,
         cd.kernel_size_x, cd.kernel_size_y,
         cd.input_channel_end - cd.input_channel_begin,
         cd.kernel_size_t)

def GetOutputShape(image_size_y, image_size_x, conv_desc):
  _, kernel_size_y, kernel_size_x, stride_y, stride_x, padding_y, padding_x = GetConvDescTuple(conv_desc)
  num_modules_y = (image_size_y + 2 * padding_y - kernel_size_y) / stride_y + 1
  num_modules_x = (image_size_x + 2 * padding_x - kernel_size_x) / stride_x + 1
  return num_modules_y, num_modules_x

def GetOutputShape4D(input_shape, conv_desc):
  batch_size, image_size_x, image_size_y, num_input_channels = input_shape
  num_output_channels, kernel_size_y, kernel_size_x, stride_y, stride_x, padding_y, padding_x = GetConvDescTuple(conv_desc)
  num_modules_y = (image_size_y + 2 * padding_y - kernel_size_y) / stride_y + 1
  num_modules_x = (image_size_x + 2 * padding_x - kernel_size_x) / stride_x + 1
  return batch_size, num_modules_x, num_modules_y, num_output_channels

def GetOutputShape5D(input_shape, conv_desc):
  batch_size, image_size_x, image_size_y, num_input_channels, image_size_t = input_shape
  num_output_channels, kernel_size_y, kernel_size_x, kernel_size_t, stride_y, stride_x, stride_t, padding_y, padding_x, padding_t = GetConvDescTuple3D(conv_desc)
  num_modules_y = (image_size_y + 2 * padding_y - kernel_size_y) / stride_y + 1
  num_modules_x = (image_size_x + 2 * padding_x - kernel_size_x) / stride_x + 1
  num_modules_t = (image_size_t + 2 * padding_t - kernel_size_t) / stride_t + 1
  return batch_size, num_modules_x, num_modules_y, num_output_channels, num_modules_t

class rnd_struct(ct.Structure):
    _fields_ = [('dev_rnd_mults', ct.POINTER(ct.c_uint)), 
                ('dev_rnd_words', ct.POINTER(ct.c_longlong))]

class sparse_data(ct.Structure):
    _fields_ = [('indptr', ct.POINTER(ct.c_int)),
                ('indices', ct.POINTER(ct.c_int)),
                ('data', ct.POINTER(ct.c_float))]

class cudamat_sparse(ct.Structure):
    _fields_ = [('data_host', sparse_data),
                ('data_device', sparse_data),
                ('on_device', ct.c_int),
                ('on_host', ct.c_int),
                ('size', ct.c_int * 2),
                ('is_trans', ct.c_int),
                ('owns_data', ct.c_int),
                ('nnz', ct.c_int)]


class TransposedCUDAMatrix(object):
    def __init__(self, mat):
        self.mat = cudamat()
        ct.memmove(ct.pointer(self.mat), ct.pointer(mat), ct.sizeof(self.mat))
        self.mat.is_trans = 1
        self.p_mat = ct.pointer(self.mat)

class SparseCUDAMatrix(object):
  """ A SparseCUDAMatrix object represents a scipy.sparse.csr matrix of single
  precision floats on a GPU.
  """
  def __init__(self, array, copy_to_device = True):
      """
    Initializes a new matrix object in one of two ways. If array is a numpy
    ndarray, memory for a matrix with the same dimensions is allocated on
    the GPU. If the copy_to_device flag is set to True, the GPU matrix is
    initialized with the given ndarray. If array is not an ndarray, it must
    be a cudamat structure (typically the user will never use this way of
    calling __init__).
    """

      assert(type(array) == sp.csr_matrix)
      self.mat = cudamat_sparse()
      self.size = self.mat.size
      self.p_mat = ct.pointer(self.mat)
      self.scipy_array = array.astype('float32')

      _cudamat.init_from_sparse_array(self.p_mat,
                                      self.scipy_array.data.ctypes.data_as(ct.POINTER(ct.c_float)),
                                      self.scipy_array.indices.ctypes.data_as(ct.POINTER(ct.c_int)),
                                      self.scipy_array.indptr.ctypes.data_as(ct.POINTER(ct.c_int)),
                                      ct.c_int(self.scipy_array.shape[0]), ct.c_int(self.scipy_array.shape[1]),
                                      ct.c_int(self.scipy_array.nnz))
      if copy_to_device:
          if err_code := _cudamat.copy_sparse_to_device(self.p_mat):
              raise generate_exception(err_code)

      # Keep a reference to free device memory in case of a crash.
      self.__free_device_memory = _cudamat.free_device_memory

class CUDAMatrix(object):
    """
    A CUDAMatrix object represents a matrix of single precision floating point
    numbers on a GPU.
    """

    def overwrite(self, array, copy_to_device=True):
        """Overwrites self with array.
        
        'array' should have a size smaller than that of the array used to
        initialize the CUDAMatrix. The method will not throw an Exception just
        yet if this is not true. It will throw exceptions or behave in strange
        ways later on.
        """
        assert type(array) == np.ndarray, 'array must be a np.ndarray.'
        array = reformat(array)
        self.numpy_array = array
        _cudamat.init_from_array(self.p_mat, array.ctypes.data_as(ct.POINTER(ct.c_float)), ct.c_int(array.shape[0]), ct.c_int(array.shape[1]))
        _cudamat.set_on_device(self.p_mat)
        if copy_to_device:
            if err_code := _cudamat.copy_to_device(self.p_mat):
                raise generate_exception(err_code)


    def __init__(self, array, copy_to_device = True, transpose = False, shape=None):
        """
        Initializes a new matrix object in one of two ways. If array is a numpy
        ndarray, memory for a matrix with the same dimensions is allocated on
        the GPU. If the copy_to_device flag is set to True, the GPU matrix is
        initialized with the given ndarray. If array is not an ndarray, it must
        be a cudamat structure (typically the user will never use this way of
        calling __init__).
        """

        if type(array) == np.ndarray:
            # Convert array to float32 in FORTRAN order
            if transpose:
              cols = array.shape[0]
              rows = array.shape[1]
            else:
              array = reformat(array)
              rows = array.shape[0]
              cols = array.shape[1]

            # Initialize as a ndarray-tied matrix.
            self.mat = cudamat()
            self.size = self.mat.size
            self.p_mat = ct.pointer(self.mat)
            self.numpy_array = array
            _cudamat.init_from_array(self.p_mat, array.ctypes.data_as(ct.POINTER(ct.c_float)), ct.c_int(rows), ct.c_int(cols))
            if copy_to_device:
                if err_code := _cudamat.copy_to_device(self.p_mat):
                    raise generate_exception(err_code)

        else:
            # Initialize based on existing cudamat structure.
            mat = array
            self.mat = mat
            self.p_mat = ct.pointer(self.mat)

        self.T = TransposedCUDAMatrix(self.mat)
        self.shape4d_ = Shape4D()
        self.p_shape4d = ct.pointer(self.shape4d_)
        if shape is None:
          self.set_shape4d((self.shape[0], 1, 1, self.shape[1]))
        else:
          self.set_shape4d(shape)

        # Keep a reference to free device memory in case of a crash.
        self.__free_device_memory = _cudamat.free_device_memory


    @staticmethod
    def init_random(seed = 0):
        """
        Initialize and seed the random number generator.
        """

        NUM_RND_STREAMS = 96*128
        CUDAMatrix.rndInitialized = 1
        CUDAMatrix.rnd_state = rnd_struct()
        CUDAMatrix.rnd_state_p = ct.pointer(CUDAMatrix.rnd_state)

        if err_code := _cudamat.init_random(
            CUDAMatrix.rnd_state_p, ct.c_int(seed)
        ):
            raise generate_exception(err_code)

    @property
    def shape(self):
        return (self.mat.size[0], self.mat.size[1])

    @property
    def shape4d(self):
        return (self.shape4d_.shape[0], self.shape4d_.shape[1],
                self.shape4d_.shape[2], self.shape4d_.shape[3]) 

    def set_shape4d(self, shape):
        if len(shape) == 2:
            s1 = ct.c_uint(shape[0])
            s2 = ct.c_uint(1)
            s3 = ct.c_uint(1)
            s4 = ct.c_uint(shape[1])
        elif len(shape) == 4:
            assert (
                shape[0] * shape[1] * shape[2] * shape[3]
                == self.shape[0] * self.shape[1]
            ), f"{shape} {self.shape}"
            s1 = ct.c_uint(shape[0])
            s2 = ct.c_uint(shape[1])
            s3 = ct.c_uint(shape[2])
            s4 = ct.c_uint(shape[3])
        elif len(shape) == 5:
            assert (
                shape[0] * shape[1] * shape[2] * shape[3] * shape[4]
                == self.shape[0] * self.shape[1]
            ), f"{shape} {self.shape}"
            s1 = ct.c_uint(shape[0])
            s2 = ct.c_uint(shape[1])
            s3 = ct.c_uint(shape[2])
            s4 = ct.c_uint(shape[3] * shape[4])

        if err_code := _cudamat.set_shape4d(self.p_shape4d, s1, s2, s3, s4):
            raise generate_exception(err_code)

        return self

    def set_shape(self, shape):
        """
        Sets the shape of the array to the given array.
        Highly unsafe method. Does no checking.
        Do not use this unless you know what you are doing.
        """
        m = ct.c_uint(shape[0])
        n = ct.c_uint(shape[1])

        if err_code := _cudamat.set_shape(self.p_mat, m, n):
            raise generate_exception(err_code)

        return self

    def reshape(self, shape):
        """
        Reshapes self to have the given shape. The number of elements cannot
        change as this only changes how the contents are interpreted.
        """
        m, n = shape
        mlen = self.shape[0] * self.shape[1]
        if m == -1:
          assert n > 0 and mlen % n == 0
          m = mlen / n
        elif n == -1:
          assert m > 0 and mlen % m == 0
          n = mlen / m

        if err_code := _cudamat.reshape(self.p_mat, ct.c_uint(m), ct.c_uint(n)):
            raise generate_exception(err_code)
        if err_code := _cudamat.reshape(self.T.p_mat, ct.c_uint(m), ct.c_uint(n)):
            raise generate_exception(err_code)

        return self

    def blockify(self, blocksize, target = None):
        if target is None:
            target = self

        if err_code := _cudamat.blockify(
            self.p_mat, target.p_mat, ct.c_uint(blocksize)
        ):
            raise generate_exception(err_code)

        return target

    def generate_translations(self, source_w, target_w, off_x, off_y, target = None):
        num_channels = self.shape[0] / source_w**2

        if target is None:
            batch_s = self.shape[1]
            target = empty((target_w**2, batch_s))

        if err_code := _cudamat.generate_translations_big_var_off(
            self.p_mat,
            target.p_mat,
            off_x.p_mat,
            off_y.p_mat,
            ct.c_uint(source_w),
            ct.c_uint(target_w),
            ct.c_uint(num_channels),
        ):
            raise generate_exception(err_code)

        return target

    def asarray(self):
        """
        Copies the matrix to an ndarray on the CPU and returns it.
        """

        self.copy_to_host()

        return self.numpy_array

    def copy_to_device(self):
        """
        Copy the matrix to the GPU.
        """

        if err_code := _cudamat.copy_to_device(self.p_mat):
            raise generate_exception(err_code)

    def copy_to_host(self):
        """
        Copy the matrix to the CPU.
        """

        if not self.mat.on_host:
            # allocate host storage if necessary
            m = self.mat.size[0]
            n = self.mat.size[1]

            self.numpy_array = np.empty((m, n), dtype=np.float32, order = 'F')
            self.mat.data_host = self.numpy_array.ctypes.data_as(ct.POINTER(ct.c_float))

            self.mat.on_host = 1

        if err_code := _cudamat.copy_to_host(self.p_mat):
            raise generate_exception(err_code)

    def assign(self, val):
        """Assign val to self, where val can be a scalar or a CUDAMatrix
        with the same dimensions as self. """

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.copy_on_device(val.p_mat, self.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.assign_scalar(self.p_mat, ct.c_float(val))
        else:
            raise ValueError, "Assigned value must be of type CUDAMatrix, int, or float."
            
        if err_code:
            raise generate_exception(err_code)

        return self

    def write_value(self, row, col, val):
        """Assign val to self[row, col], where val is a scalar. """

        if err_code := _cudamat.write_at(self.p_mat, row, col, ct.c_float(val)):
            raise generate_exception(err_code)

        return self

    def read_value(self, row, col):
        """Assign val to self[row, col], where val is a scalar. """

        err_code = ct.c_int(0)
        res = _cudamat.read_from(self.p_mat, row, col, ct.byref(err_code))
            
        if err_code:
            raise generate_exception(err_code)

        return res

    def free_device_memory(self):
        """
        Free memory used up by the matrix on the GPU.
        """

        if err_code := _cudamat.free_device_memory(self.p_mat):
            raise generate_exception(err_code)

    def set_trans(self, is_trans):
        """
        Set the transposedness flag to is_trans.
        """

        _cudamat.set_transpose(self.p_mat, ct.c_int(1 * is_trans))

    def col_slice(self, first_col, last_col):
        mat = cudamat()

        if err_code := _cudamat.get_slice(
            self.p_mat, ct.pointer(mat), ct.c_int(first_col), ct.c_int(last_col)
        ):
            raise generate_exception(err_code)

        new_mat = CUDAMatrix(mat)

        try:
            new_mat.sliceof = self.sliceof
        except:
            new_mat.sliceof = self

        return new_mat


    def slice(self, first_col, last_col):
        mat = cudamat()

        if self.mat.size[0] == 1 or self.mat.size[1] == 1:
            err_code = _cudamat.get_vector_slice(self.p_mat, ct.pointer(mat), ct.c_int(first_col), ct.c_int(last_col))
        else:
            err_code = _cudamat.get_slice(self.p_mat, ct.pointer(mat), ct.c_int(first_col), ct.c_int(last_col))

        if err_code:
            raise generate_exception(err_code)

        new_mat = CUDAMatrix(mat)

        try:
            new_mat.sliceof = self.sliceof
        except:
            new_mat.sliceof = self

        return new_mat

    def get_col_slice(self, first_col, last_col, target = None):
        col_slice = self.slice(first_col, last_col)

        if not target:
            return col_slice
        target.assign(col_slice)
        return target

    def set_col_slice(self, first_col, last_col, mat):
        self.slice(first_col, last_col).assign(mat)

        return self

    def get_row_slice(self, start, end, target = None):
        """
        Get the rows with indices start through end. If target is not provided
        memory for a new matrix will be allocated.
        """

        width = self.shape[1]

        if not target:
            target = empty((end-start, width))

        if err_code := _cudamat.get_row_slice(
            self.p_mat, target.p_mat, ct.c_int(start), ct.c_int(end)
        ):
            raise generate_exception(err_code)

        return target

    def set_row_slice(self, start, end, mat):
        """
        Assign the contents of mat to the rows with indices start through end.
        """

        if err_code := _cudamat.set_row_slice(
            mat.p_mat, self.p_mat, ct.c_int(start), ct.c_int(end)
        ):
            raise generate_exception(err_code)

        return self

    def transpose(self, target = None):
        """
        Return a transposed copy of the matrix.
        """
        if not target:
            target = empty((self.shape[1], self.shape[0]))

        if err_code := _cudamat.copy_transpose(self.p_mat, target.p_mat):
            raise generate_exception(err_code)

        return target

    def fill_with_rand(self):
        """
        Fill matrix on the GPU with random numbers drawn from the uniform
        distribution over the (0,1) interval.
        """

        if err_code := _cudamat.fill_with_rand(CUDAMatrix.rnd_state_p, self.p_mat):
            raise generate_exception(err_code)

        return self

    def fill_with_randn(self):
        """
        Fill matrix on the GPU with random numbers drawn from the standard normal
        distribution.
        """

        if err_code := _cudamat.fill_with_randn(
            CUDAMatrix.rnd_state_p, self.p_mat
        ):
            raise generate_exception(err_code)

        return self

    def dropout(self, dropprob, val=0.0, scale=1.0):
        """
        Drop entries in this matrix uniformly randomly with given probability
        and set the dropped out unit to state val.
        """
        if err_code := _cudamat.dropout(
            CUDAMatrix.rnd_state_p,
            self.p_mat,
            ct.c_float(dropprob),
            ct.c_float(val),
            ct.c_float(scale),
        ):
            raise generate_exception(err_code)

        return self

    def sample_bernoulli(self, target=None):
        """
        Sample a bernoulli distribution. Choose 1 with probability given by entries of self, 0 otherwise.
        """
        if not target:
          target = self
        if err_code := _cudamat.sample_bernoulli(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return self

    def sample_bernoulli_tanh(self, target=None):
        """
        Sample a bernoulli distribution. Choose 1 with probability given by entries of (1+self)/2, -1 otherwise.
        """
        if not target:
          target = self
        if err_code := _cudamat.sample_bernoulli_tanh(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return self

    def sample_poisson(self, target=None):
        """
        Sample a poisson distribution. Choose 1 with probability given by entries of self.
        Not implemented yet.
        """
        if not target:
          target = self
        if err_code := _cudamat.sample_poisson(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return self

    def sample_gaussian(self, mult=1.0, target=None):
        """
        Add zero mean gaussian noise to the matrix. mult is the stddev.
        """
        if not target:
          target = self
        if err_code := _cudamat.sample_gaussian(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat, ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return self

    def perturb_energy_for_softmax_sampling(self, target=None):
        """
        Add by -log(-log(rand)).
        """
        if not target:
          target = self
        if err_code := _cudamat.perturb_energy(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return self

    def perturb_prob_for_softmax_sampling(self, target=None):
        """
        Divide by -log(rand).
        """
        if not target:
          target = self
        if err_code := _cudamat.perturb_prob(
            CUDAMatrix.rnd_state_p, self.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return self


    def add_col_vec(self, vec, target = None):
        """
        Add vector vec to every column of the matrix. If a target is provided,
        it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.add_col_vec(self.p_mat, vec.p_mat, target.p_mat):
            raise generate_exception(err_code)

        return target
        
    def add_col_mult(self, vec, mult, target = None):
        """
        Add a multiple of vector vec to every column of the matrix. If a target
        is provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.add_col_mult(
            self.p_mat, vec.p_mat, target.p_mat, ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return target

    def mult_diagonal(self, val, target = None):
        """
        Mult val to the diagonal of self. If a target
        is provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        assert self.shape[0] == self.shape[1], 'self must be a square matrix'
        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.mult_diagonal(self.p_mat, val.p_mat, target.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.mult_diagonal_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target



    def add_diagonal(self, val, target = None):
        """
        Add val to the diagonal of self. If a target
        is provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        assert self.shape[0] == self.shape[1], 'self must be a square matrix'
        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.add_diagonal(self.p_mat, val.p_mat, target.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.add_diagonal_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target


    def add_row_mult(self, vec, mult, target = None):
        """
        Add a multiple of vector vec to every row of the matrix. If a target
        is provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.add_row_mult(
            self.p_mat, vec.p_mat, target.p_mat, ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return target
        
    def add_row_vec(self, vec, target = None):
        """
        Add vector vec to every row of the matrix. If a target is provided,
        it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.add_row_vec(self.p_mat, vec.p_mat, target.p_mat):
            raise generate_exception(err_code)

        return target
        
    def mult_by_col(self, vec, target = None):
        """
        Multiply vector vec into every column of the matrix. If a target is
        provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.mult_by_col_vec(
            self.p_mat, vec.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return target
        
    def mult_by_row(self, vec, target = None):
        """
        Multiply vector vec into every row of the matrix. If a target is
        provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.mult_by_row_vec(
            self.p_mat, vec.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return target

    def div_by_col(self, vec, target = None):
        """
        Multiply vector vec into every column of the matrix. If a target is
        provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.div_by_col_vec(
            self.p_mat, vec.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return target
        
    def div_by_row(self, vec, target = None):
        """
        Divide vector vec into every row of the matrix. If a target is
        provided, it is used to store the result instead of self.
        """

        if not target:
            target = self

        if err_code := _cudamat.div_by_row_vec(
            self.p_mat, vec.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return target
 
    def sum(self, axis=None, target = None, mult=1.0):
        """
        Sum the matrix along the given dimension, where 0 represents the leading
        dimension and 1 represents the non-leading dimension. If None, the sum
        of all elements is returned. If a target is not prvided, a new vector is
        created for storing the result.
        """
        if axis is not None:
            return sum(self, axis, target, mult)
        """
          err_code = ct.c_int(0)
          res = _cudamat.sum_all(self.p_mat, ct.byref(err_code))
          if err_code:
              raise generate_exception(err_code)
          return res
          """
        return vdot(self, CUDAMatrix.ones.slice(0, self.shape[0]*self.shape[1])) * mult

    def sum_along_cols(self, target = None, mult=1.0):
        """
        Sum the matrix along the given dimension, where 0 represents the leading
        dimension and 1 represents the non-leading dimension. If None, the sum
        of all elements is returned. If a target is not prvided, a new vector is
        created for storing the result.
        """
        m = self.shape[0]
        if not target:
            target = empty((m, 1))
        if err_code := _cudamat.sum_by_axis(
            self.p_mat, target.p_mat, 1, ct.c_float(mult), 0
        ):
            raise generate_exception(err_code)
        return target


    def add_sums(self, mat, axis, mult = 1.):
        """
        Add a multiple of the sums of the matrix mat along the given dimension
        to self. 
        """

        m = _cudamat.get_leading_dimension(mat.p_mat)
        n = _cudamat.get_nonleading_dimension(mat.p_mat)

        if axis == 0:
            # sum along leading dimension
            left = CUDAMatrix.ones.slice(0, m)
            left.set_trans(True)
            right = mat

        elif axis == 1:
            # sum along non-leading dimension
            left = mat
            right = CUDAMatrix.ones.slice(0, n)

        if err_code := _cudamat.dot(
            left.p_mat, right.p_mat, self.p_mat, ct.c_float(1.0), ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return self

    def less_than_eq(self, val, target = None):
        """
        Perform the operation target = 1. * (self < val), where val can be a matrix or a scalar.
        """

        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.less_than_eq_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.less_than_eq(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def less_than(self, val, target = None):
        """
        Perform the operation target = 1. * (self < val), where val can be a matrix or a scalar.
        """

        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.less_than_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.less_than(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def greater_than_eq(self, val, target = None):
        """
        Perform the operation target = 1. * (self > val), where val can be a matrix or a scalar.
        """

        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.greater_than_eq_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.greater_than_eq(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def greater_than(self, val, target = None):
        """
        Perform the operation target = 1. * (self > val), where val can be a matrix or a scalar.
        """

        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.greater_than_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.greater_than(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def upper_bound(self, val, target = None):
        """
        Perform the operation target = (self > val) ? val:self, where val can be a matrix or a scalar.
        """
        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.upper_bound_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.upper_bound(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def upper_bound_mod(self, val, target = None):
        """
        Perform the operation target = (|self| > val) ? sign(self)*val:self, where val can be a matrix or a scalar.
        """
        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.upper_bound_mod_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.upper_bound(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target


    def lower_bound(self, val, target = None):
        """
        Perform the operation target = (self < val) ? val:self, where val can be a matrix or a scalar.
        """
        if not target:
            target = self

        if isinstance(val, (int, float)):
            err_code = _cudamat.lower_bound_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            err_code = _cudamat.lower_bound(self.p_mat, val.p_mat, target.p_mat)

        if err_code:
            raise generate_exception(err_code)

        return target

    def cumsum(self, axis, temp=None, target = None):
        """
        Cumulative sum along axis.
        """

        m, n = self.shape
        assert axis == 0, 'axis = 1 not implemented.'
        if not target:
            target = empty((m, n))
        if not temp:
            temp = empty((m, n))
        """ 
        elif axis == 1:
            if not target:
                target = empty((m, 1))
        """ 

        if err_code := _cudamat.cumsum_by_axis(
            self.p_mat, target.p_mat, temp.p_mat, ct.c_int(axis)
        ):
            raise generate_exception(err_code)

        return target

    def choose_max_and_accumulate(self, acc):
        """
        Find the maximum value along the given dimension, where 0 represents the
        leading dimension and 1 represents the non-leading dimension. If a target
        is not prvided, a new vector is created for storing the result.
        """

        m, n = self.shape

        if err_code := _cudamat.choose_max_and_accumulate(self.p_mat, acc.p_mat):
            raise generate_exception(err_code)

        return acc


    def choose_max(self, axis, target = None):
        """
        Sets the argmax along axis to 1 and rest to zero.
        """

        m, n = self.shape

        assert axis == 0, 'Axis = 1 not implemented.'
        if not target:
          target = self

        if err_code := _cudamat.choose_max_by_axis(
            self.p_mat, target.p_mat, ct.c_int(axis)
        ):
            raise generate_exception(err_code)

        return target


    def max(self, axis, target = None):
        """
        Find the maximum value along the given dimension, where 0 represents the
        leading dimension and 1 represents the non-leading dimension. If a target
        is not prvided, a new vector is created for storing the result.
        """

        m, n = self.shape

        if axis == 0:
            if not target:
                target = empty((1, n))

        elif axis == 1:
            if not target:
                target = empty((m, 1))

        if err_code := _cudamat.max_by_axis(
            self.p_mat, target.p_mat, ct.c_int(axis)
        ):
            raise generate_exception(err_code)

        return target

    def argmax(self, axis, target = None):
        """
        Find the index with the maximum value along the given dimension, where 0 represents the
        leading dimension and 1 represents the non-leading dimension. If a target
        is not prvided, a new vector is created for storing the result.
        """

        m, n = self.shape

        if axis == 0:
            if not target:
                target = empty((1, n))

        elif axis == 1:
            if not target:
                target = empty((m, 1))

        if err_code := _cudamat.argmax_by_axis(
            self.p_mat, target.p_mat, ct.c_int(axis)
        ):
            raise generate_exception(err_code)

        return target

    def add_sqsums(self, mat, axis, mult = 1.):
        """
        Add the sum of squares of mat along the given dimension to self. 0 represents the
        leading dimension and 1 represents the non-leading dimension.
        """
        m, n = mat.shape
        if axis == 0:
            assert self.shape == (
                1,
                n,
            ), f'Self has shape {self.shape} but mat has shape {mat.shape}'
        elif axis == 1:
            assert self.shape == (m, 1)

        if err_code := _cudamat.sqsum_by_axis(
            mat.p_mat,
            self.p_mat,
            ct.c_int(axis),
            ct.c_float(mult),
            ct.c_float(1.0),
        ):
            raise generate_exception(err_code)

    def sqsum(self, axis, target = None, mult=1.0):
        """
        Find the sum of squares along the given dimension, where 0 represents the
        leading dimension and 1 represents the non-leading dimension. If a target
        is not prvided, a new vector is created for storing the result.
        """

        m, n = self.shape

        if axis == 0:
            if not target:
                target = empty((1, n))

        elif axis == 1:
            if not target:
                target = empty((m, 1))

        if err_code := _cudamat.sqsum_by_axis(
            self.p_mat,
            target.p_mat,
            ct.c_int(axis),
            ct.c_float(mult),
            ct.c_float(0.0),
        ):
            raise generate_exception(err_code)

        return target

    def norm_limit(self, norm, axis, target = None, constraint=0):
        """
        Limit the norm along the given dimension to be 'norm', where 0
        represents the leading dimension and 1 represents the non-leading
        dimension. If a target is not provided, self is used as target.
        """
        m, n = self.shape

        if not target:
            target = self

        if err_code := _cudamat.normlimit_by_axis(
            self.p_mat,
            target.p_mat,
            ct.c_int(axis),
            ct.c_float(norm),
            ct.c_int(constraint),
        ):
            raise generate_exception(err_code)

        return target


    def apply_softmax(self, target = None):
        """
        Apply the softmax activation function.
        """
        return softmax(self, target)

    def apply_softmax_row_major(self, num_slices = None):
        """
        Apply the softmax activation function.
        """
        if num_slices is None:
          num_slices = self.shape[1]
        if err_code := _cudamat.softmax_row_major_multi(
            self.p_mat, ct.c_int(num_slices)
        ):
            raise generate_exception(err_code)
        return self

    def sign(self, target = None):
        """
        Find the sign of each element of the matrix.
        """

        if not target:
            target = empty((self.mat.size[0], self.mat.size[1]))

        if err_code := _cudamat.sign(self.p_mat, target.p_mat):
            raise generate_exception(err_code)

        return target

    def apply_cos(self, target = None):
        """
        Apply the cos sigmoid to each element of the matrix.
        """

        return cos(self, target)

    def apply_sin(self, target = None):
        """
        Apply the sin sigmoid to each element of the matrix.
        """

        return sin(self, target)

    def apply_sigmoid(self, target = None):
        """
        Apply the logistic sigmoid to each element of the matrix.
        """

        return sigmoid(self, target)

    def reciprocal(self, target = None):
        """
        Find the reciprocal of each element of the matrix.
        """

        if not target:
            target = self

        if err_code := _cudamat.reciprocal(self.p_mat, target.p_mat):
            raise generate_exception(err_code)

        return target

    def dot(self, mat2, mult=1.0, target = None):
        """
        Multiply the matrix by mat2 from the right and multiply by scalar mult.
        """

        return dot(self, mat2, mult, target)

    def add_dot(self, m1, m2, mult=1.0):
        """
        Add the dot product of m1 and m2 to the matrix.
        """

        if err_code := _cudamat.dot(
            m1.p_mat, m2.p_mat, self.p_mat, ct.c_float(1.0), ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return self

    def subtract_dot(self, m1, m2):
        """
        Subtract the dot product of m1 and m2 from the matrix.
        """

        if err_code := _cudamat.dot(
            m1.p_mat, m2.p_mat, self.p_mat, ct.c_float(1.0), ct.c_float(-1.0)
        ):
            raise generate_exception(err_code)

        return self

    def add_mult_sign(self, mat2, mult = 1.):
        """
        Add multiple of sign of mat2 to the matrix.
        """

        if err_code := _cudamat.add_mult_sign(
            self.p_mat, mat2.p_mat, ct.c_float(mult)
        ):
            raise generate_exception(err_code)

        return self

    def add_mult(self, mat2, mult = 1.):
        """
        Add multiple of mat2 to the matrix.
        """

        if err_code := _cudamat.add_mult(self.p_mat, mat2.p_mat, ct.c_float(mult)):
            raise generate_exception(err_code)

        return self
    
    def subtract_mult(self, mat2, mult = 1.):
        """
        Subtract a multiple of mat2 from the matrix.
        """

        if err_code := _cudamat.add_mult(
            self.p_mat, mat2.p_mat, ct.c_float(-1.0 * mult)
        ):
            raise generate_exception(err_code)

        return self

    def add(self, val, target = None):
        """Add val to self, where val can be a scalar or a CUDAMatrix with the
        same dimensions as self. """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.add_elementwise(self.p_mat, val.p_mat, target.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.add_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target

    def accumulate_columns(self, indices, target, mult=1.0, avg=False):
        if not target:
            target = self
        avgg = 1 if avg else 0
        if err_code := _cudamat.accumulate_columns(
            self.p_mat,
            indices.p_mat,
            target.p_mat,
            ct.c_float(mult),
            ct.c_int(avgg),
        ):
            raise generate_exception(err_code)
        return target

    def expand(self, expansion_indices, target):

        if err_code := _cudamat.expand(
            self.p_mat, expansion_indices.p_mat, target.p_mat
        ):
            raise generate_exception(err_code)

        return target

    def expand_and_add(self, val, expansion_indices, target = None, mult=1.0):

        if not target:
            target = self

        if isinstance(val, CUDAMatrix) and isinstance(expansion_indices, CUDAMatrix):
            err_code = _cudamat.expand_and_add(self.p_mat, val.p_mat, expansion_indices.p_mat, target.p_mat, ct.c_float(mult))
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target

    def subtract(self, val, target = None):
        """Subtract val from self, where val can be a scalar or a CUDAMatrix with
        the same dimensions as self. """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.subtract_elementwise(self.p_mat, val.p_mat, target.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.add_scalar(self.p_mat, ct.c_float(-1*val), target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target

    def divide(self, val, target = None):
        """Divide self by val, where val can be a scalar or a CUDAMatrix with the
        same dimensions as self. """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.divide_elementwise(self.p_mat, val.p_mat, target.p_mat)
        elif isinstance(val, (int, float)):
            err_code = _cudamat.divide_by_scalar(self.p_mat, ct.c_float(val), target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target

    def mult(self, val, target = None, scale_targets=0.0):
        """Multiply self by val, where val can be a scalar or a CUDAMatrix with
        the same dimensions as self. """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.mult_elementwise(self.p_mat, val.p_mat, target.p_mat, ct.c_float(scale_targets))
        elif isinstance(val, (int, float)):
            err_code = _cudamat.mult_by_scalar(self.p_mat, ct.c_float(val), target.p_mat, ct.c_float(scale_targets))
        else:
            raise ValueError, "Value must be of type CUDAMatrix, int, or float."

        if err_code:
            raise generate_exception(err_code)

        return target

    def apply_cos_deriv(self, val, target = None):
        """
        Apply cos derivative, where val is the activation of cos units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_cos_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target


    def apply_sin_deriv(self, val, target = None):
        """
        Apply sin derivative, where val is the activation of sin units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_sin_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def get_softmax_correct(self, labels, target):
        """
        target[i] = 1, iff labels[i] is correctly predicted; 0 otherwise.
        """
        assert labels.shape == (1, self.shape[1])
        assert target.shape == labels.shape
        if isinstance(labels, CUDAMatrix):
            err_code = _cudamat.get_softmax_correct(self.p_mat, labels.p_mat, target.p_mat)
        else:
            raise ValueError, "labels must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def get_softmax_correct_row_major(self, labels, target):
        """
        target[i] = 1, iff labels[i] is correctly predicted; 0 otherwise.
        """
        assert labels.shape == (self.shape[0], 1), 'Labels shape %d-%d, softmax shape %d-1' % (labels.shape[0], labels.shape[1])
        assert target.shape == labels.shape
        if isinstance(labels, CUDAMatrix):
            err_code = _cudamat.get_softmax_correct_row_major(self.p_mat, labels.p_mat, target.p_mat)
        else:
            raise ValueError, "labels must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def get_softmax_cross_entropy(self, labels, target, tiny=1e-10):
        """
        target[i] = -log(self[label[i]] + tiny).
        """
        assert labels.shape == (1, self.shape[1])
        assert target.shape == labels.shape
        if isinstance(labels, CUDAMatrix):
            err_code = _cudamat.get_softmax_cross_entropy(self.p_mat, labels.p_mat, target.p_mat, ct.c_float(tiny))
        else:
            raise ValueError, "labels must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target



    def apply_softmax_grad(self, labels, target = None):
        """
        Apply softmax derivative, where labels are the correct labels.
        """
        if not target:
            target = self

        assert labels.shape == (1, self.shape[1])
        assert target.shape == self.shape
        if isinstance(labels, CUDAMatrix):
            err_code = _cudamat.apply_softmax_grad(self.p_mat, labels.p_mat, target.p_mat)
        else:
            raise ValueError, "labels must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def apply_softmax_grad_row_major(self, labels, target = None):
        """
        Apply softmax derivative, where labels are the correct labels.
        """
        if not target:
            target = self

        assert labels.shape == (self.shape[0], 1)
        assert target.shape == self.shape
        if isinstance(labels, CUDAMatrix):
            err_code = _cudamat.apply_softmax_grad_row_major(self.p_mat, labels.p_mat, target.p_mat)
        else:
            raise ValueError, "labels must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target



    def apply_logistic_deriv(self, val, target = None):
        """
        Apply logistic derivative, where val is the activation of logistic units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_logistic_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def apply_tanh_deriv(self, val, target = None):
        """
        Apply tanh derivative, where val is the activation of the units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_tanh_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def apply_rectified_linear_deriv(self, val, target = None):
        """
        Apply rectified linear derivative, where val is the activation of the units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_rectified_linear_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    def apply_rectified_linear_smooth_deriv(self, val, target = None):
        """
        Apply rectified linear smooth derivative, where val is the activation of the units.
        """

        if not target:
            target = self

        if isinstance(val, CUDAMatrix):
            err_code = _cudamat.apply_rectified_linear_smooth_deriv(self.p_mat, val.p_mat, target.p_mat)
        else:
            raise ValueError, "Value must be of type CUDAMatrix."

        if err_code:
            raise generate_exception(err_code)

        return target

    @deprecated
    def assign_scalar(self, alpha):
        """
        Assign scalar alpha to every element of the matrix.
        """

        if err_code := _cudamat.assign_scalar(self.p_mat, ct.c_float(alpha)):
            raise generate_exception(err_code)

        return self

    @deprecated
    def mult_by_scalar(self, alpha, target = None):
        """
        Multiply the matrix by a scalar.
        """

        if not target:
            target = self

        if err_code := _cudamat.mult_by_scalar(
            self.p_mat, ct.c_float(alpha), target.p_mat
        ):
            raise generate_exception(err_code)

        return target


    @deprecated
    def div_by_scalar(self, alpha, target = None):
        """
        Divide the matrix by a scalar.
        """

        if not target:
            target = self

        if err_code := _cudamat.divide_by_scalar(
            self.p_mat, ct.c_float(alpha), target.p_mat
        ):
            raise generate_exception(err_code)

        return target

    @deprecated
    def add_scalar(self, alpha, target = None):
        """
        Increment the matrix by a scalar.
        """

        if not target:
            target = self

        if err_code := _cudamat.add_scalar(
            self.p_mat, ct.c_float(alpha), target.p_mat
        ):
            raise generate_exception(err_code)

        return target

    def euclid_norm(self):
        err_code = ct.c_int(0)
        res = _cudamat.euclid_norm(self.p_mat, ct.byref(err_code))

        if err_code:
            raise generate_exception(err_code.value)

        return res

    def select_columns(self, indices, target):
        """
        copies some columns of self into target.
        <indices> must be a row vector. Its elements are float32's representing integers, e.g. "34.0" means the integer "34".
        after this call, for all r,c, target[r,c]=self[r,indices[c]].
        This returns target.
        Negative indices are interpreted in the usual Python way: all elements of <indices> had better be in the range [-self.shape[1], self.shape[1]-1].
        This does bounds checking, but out of bounds indices do not raise an exception (because the programmer was lazy). Instead, they result in NaN values in <target>.
        """

        if err_code := _cudamat.selectRows(
            self.p_mat, target.p_mat, indices.p_mat
        ):
            raise generate_exception(err_code)

        return target

    def shuffle_columns(self, rand_per_indices):
        if err_code := _cudamat.shuffleColumns(self.p_mat, rand_per_indices.p_mat):
            raise generate_exception(err_code)

    def swap_columns(self, indices1, indices2, target):
        """
        swap columns at indices1 of self with columns at indices2 of target.
        <indices1> and <indices2> must be row vectors of equal length. Its elements are float32's representing integers, e.g. "34.0" means the integer "34".
        after this call, for all r,c, target[r,indices2[c]=self[r,indices1[c]].
        self can be same as target, but then the result will be non-deterministic if there is overlap between indices1 and indices2. Can be used for in-place shuffling by making sure indices1 and indices2 do not overlap.
        This returns target.
        Negative indices are interpreted in the usual Python way: all elements of <indices> had better be in the range [-self.shape[1], self.shape[1]-1].
        This does bounds checking, but out of bounds indices do not raise an exception (because the programmer was lazy). Instead, they result in NaN values in <target>.
        """
        assert indices1.shape == indices2.shape
        if err_code := _cudamat.swapColumns(
            self.p_mat, target.p_mat, indices1.p_mat, indices2.p_mat
        ):
            raise generate_exception(err_code)

        return target

    def set_selected_columns(self, indices, source):
        """
        copies all columns of source into some columns of self.
        <indices> must be a row vector. Its elements are float32's representing
        integers, e.g. "34.0" means the integer "34". after this call, for all
        r,c, self[r,indices[c]]=source[r,c]. This returns self.
        Negative indices are interpreted in the usual Python way: all elements
        of <indices> had better be in the range [-self.shape[1], self.shape[1]-1].
        This does bounds checking, but out of bounds indices do not raise an
        exception (because the programmer was lazy). Instead, they result in NaN
        values in <self>.
        """

        if err_code := _cudamat.setSelectedRows(
            self.p_mat, source.p_mat, indices.p_mat
        ):
            raise generate_exception(err_code)

        return self

def empty(shape):
    """
    Creates and returns a new CUDAMatrix with the given shape.
    """
    mat = cudamat()
    if len(shape) == 2:
      err_code = _cudamat.init_empty(ct.pointer(mat), ct.c_int(shape[0]), ct.c_int(shape[1]))
    elif len(shape) == 4:
      err_code = _cudamat.init_empty(ct.pointer(mat), ct.c_int(shape[0]), ct.c_int(shape[1] * shape[2] * shape[3]))
    elif len(shape) == 5:
      err_code = _cudamat.init_empty(ct.pointer(mat), ct.c_int(shape[0]), ct.c_int(shape[1] * shape[2] * shape[3] * shape[4]))
    else:
      raise Exception('Invalid shape.')

    if err_code:
        raise generate_exception(err_code)

    m = CUDAMatrix(mat)
    m.set_shape4d(shape)

    m.assign(0)
    return m

def empty_like(m):
    """
    Creates and returns a new CUDAMatrix with the shape same as that of m.
    """
    cmat = empty(m.shape)
    cmat.set_shape4d(m.shape4d)
    return cmat

def sum(mat, axis, target = None, mult=1.0):
    """
    Sum the matrix along the given dimension, where 0 represents the leading
    dimension and 1 represents the non-leading dimension. If a target is
    not prvided, a new vector is created for storing the result.
    """

    m = _cudamat.get_leading_dimension(mat.p_mat)
    n = _cudamat.get_nonleading_dimension(mat.p_mat)

    if axis == 0:
        # sum along leading dimension
        left = CUDAMatrix.ones.slice(0, m)
        left.set_trans(True)
        right = mat

        if not target:
            target = empty((1, n))

    elif axis == 1:
        # sum along non-leading dimension
        left = mat
        right = CUDAMatrix.ones.slice(0, n)

        if not target:
            target = empty((m, 1))

    if err_code := _cudamat.dot(
        left.p_mat,
        right.p_mat,
        target.p_mat,
        ct.c_float(0.0),
        ct.c_float(mult),
    ):
        raise generate_exception(err_code)

    return target

def sparse_dot(sparse_mat, dense_mat, mult=1.0, target = None):
    if not target:
        m = sparse_mat.size[0]
        n = dense_mat.size[1]
        target = empty((m, n))

    print target.shape
    err_code = _cudamat.sparse_dot(sparse_mat.p_mat, dense_mat.p_mat, target.p_mat, ct.c_float(0.), ct.c_float(mult))
    if err_code:
        raise generate_exception(err_code)

    return target

def dot(m1, m2, mult=1.0, target = None, scale_targets=0.0):
    """
    Find the dot product between m1 and m2.
    """

    if not target:
        m = _cudamat.get_leading_dimension(m1.p_mat)
        n = _cudamat.get_nonleading_dimension(m2.p_mat)

        target = empty((m, n))

    if err_code := _cudamat.dot(
        m1.p_mat,
        m2.p_mat,
        target.p_mat,
        ct.c_float(scale_targets),
        ct.c_float(mult),
    ):
        raise generate_exception(err_code)

    return target

def vdot(m1, m2):
    """
    Compute the vector dot product of matrices m1 and m2.
    """

    err_code = ct.c_int(0)
    res = _cudamat.vdot(m1.p_mat, m2.p_mat, ct.byref(err_code))

    if err_code:
        raise generate_exception(err_code.value)

    return res

def softmax(mat, target = None):
    """
    Apply cos to each element of the matrix mat.
    """

    if target:
      err_code = _cudamat.softmax(mat.p_mat, target.p_mat)
    else:
      err_code = _cudamat.softmax_overwrite(mat.p_mat)
      target = mat
    if err_code:
        raise generate_exception(err_code)
    return target

def cos(mat, target = None):
    """
    Apply cos to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_cos(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target



def sin(mat, target = None):
    """
    Apply sin to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_sin(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def sigmoid(mat, target = None):
    """
    Apply the logistic sigmoid to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_sigmoid(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target


def tanh(mat, target = None):
    """
    Apply the tanh to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_tanh(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def abs(mat, target = None):
    """
    Apply abs to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_abs(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def log_1_plus_exp(mat, target = None, exact=False):
    """
    Apply log(1+exp(x)) to each element of the matrix mat. If exact is True, use
    slow and accurate log and exp.
    """

    if not target:
        target = mat

    if exact:
      err_code = _cudamat.apply_log_1_plus_exp_exact(mat.p_mat, target.p_mat)
    else:
      err_code = _cudamat.apply_log_1_plus_exp(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def log(mat, tiny=0.0, target = None):
    """
    Find the natural logarithm of each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_log(mat.p_mat, target.p_mat, ct.c_float(tiny))
    if err_code:
        raise generate_exception(err_code)

    return target

def exp(mat, target = None):
    """
    Apply the exponential function to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_exp(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def ceil(mat, target = None):
    """
    Apply the ceil function to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_ceil(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def floor(mat, target = None):
    """
    Apply the floor function to each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_floor(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def sqrt(mat, target = None):
    """
    Compute the square root of each element of the matrix mat.
    """

    if not target:
        target = mat

    err_code = _cudamat.apply_sqrt(mat.p_mat, target.p_mat)
    if err_code:
        raise generate_exception(err_code)

    return target

def cross_entropy_bernoulli(mat, p, target = None, tiny=1e-10):
    """
    Compute -mat*log(p) - (1-mat).*log(1-p)
    """

    if not target:
        target = mat

    if isinstance(p, CUDAMatrix):
        err_code = _cudamat.compute_cross_entropy_bernoulli(mat.p_mat, p.p_mat, target.p_mat, ct.c_float(tiny))
    else:
        raise ValueError, "Value must be of type CUDAMatrix."

    if err_code:
        raise generate_exception(err_code)

    return target


def cross_entropy(mat, p, target = None, tiny=1e-10):
    """
    Compute -mat*log(p)
    """

    if not target:
        target = mat

    if isinstance(p, CUDAMatrix):
        err_code = _cudamat.compute_cross_entropy(mat.p_mat, p.p_mat, target.p_mat, ct.c_float(tiny))
    else:
        raise ValueError, "Value must be of type CUDAMatrix."

    if err_code:
        raise generate_exception(err_code)

    return target

def correct_preds(mat, p, target = None, cutoff=0.5):
    """
    Compute mat*(p >= 0.5) + (1-mat).*(p < 0.5)
    """

    if not target:
        target = mat

    if isinstance(p, CUDAMatrix):
        err_code = _cudamat.correct_preds(mat.p_mat, p.p_mat, target.p_mat, ct.c_float(cutoff))
    else:
        raise ValueError, "Value must be of type CUDAMatrix."

    if err_code:
        raise generate_exception(err_code)

    return target

def pow(mat, p, target = None):
    """
    If p is a scalar, compute the 'p'th power of each element of the matrix mat,
    otherwise raise each element of the matrix mat to the power given by the
    corresponding element of the matrix p.
    """

    if not target:
        target = mat

    if isinstance(p, CUDAMatrix):
        err_code = _cudamat.apply_pow_matrix(mat.p_mat, p.p_mat, target.p_mat)
    elif isinstance(p, (int, float)):
        err_code = _cudamat.apply_pow(mat.p_mat, ct.c_float(p), target.p_mat)
    else:
        raise ValueError, "Value must be of type CUDAMatrix, int, or float."

    if err_code:
        raise generate_exception(err_code)

    return target

def extract_patches(images, patches, width_offset, height_offset, flip, img_width, img_height, patch_width, patch_height):
  err_code = _cudamat.extract_patches(images.p_mat, patches.p_mat, width_offset.p_mat, height_offset.p_mat, flip.p_mat, ct.c_int(img_width), ct.c_int(img_height), ct.c_int(patch_width), ct.c_int(patch_height))
  if err_code:
    raise generate_exception(err_code)

def lstm_fprop(s_in, s_out, w_dense, w_diag, b, use_relu=False, init=False):
  numcases, num_lstms_mult = s_in.shape
  num_lstms = num_lstms_mult / 6
  assert s_out.shape == s_in.shape
  assert w_diag.shape == (1, 3 * num_lstms)
  assert w_dense.shape == (4 * num_lstms, num_lstms)
  assert b.shape == (1, 4 * num_lstms)
 
  err_code = _cudamat.lstm_fprop(s_in.p_mat, s_out.p_mat, w_dense.p_mat, w_diag.p_mat, b.p_mat, ct.c_bool(init), ct.c_bool(use_relu))
  if err_code:
    raise generate_exception(err_code)

def lstm_bprop(s_in, s_out, d_in, d_out, w_dense, w_diag, use_relu=False, init=False):
  numcases, num_lstms_mult = s_in.shape
  num_lstms = num_lstms_mult / 6
  assert s_out.shape == s_in.shape
  assert d_in.shape  == s_in.shape
  assert d_out.shape == s_in.shape
  assert w_diag.shape == (1, 3 * num_lstms)
  assert w_dense.shape == (4 * num_lstms, num_lstms)

  err_code = _cudamat.lstm_bprop(s_in.p_mat, s_out.p_mat, d_in.p_mat, d_out.p_mat, w_dense.p_mat, w_diag.p_mat, ct.c_bool(init), ct.c_bool(use_relu))
  if err_code:
    raise generate_exception(err_code)

def lstm_outp(s_in, s_out, d_out, dw_dense, dw_diag, db, init=False):
  numcases, num_lstms_mult = s_in.shape
  num_lstms = num_lstms_mult / 6
  assert s_out.shape == s_in.shape
  assert d_out.shape == s_in.shape
  assert dw_diag.shape == (1, 3 * num_lstms)
  assert dw_dense.shape == (4 * num_lstms, num_lstms)
  assert db.shape == (1, 4 * num_lstms)

  err_code = _cudamat.lstm_outp(s_in.p_mat, s_out.p_mat, d_out.p_mat, dw_dense.p_mat, dw_diag.p_mat, db.p_mat, ct.c_bool(init))
  if err_code:
    raise generate_exception(err_code)

def cuda_sync_threads():
    _cudamat.cuda_sync_threads()

def reformat(array):
    """
    Returns array as a float32 array in FORTRAN order.
    """

    return np.array(array, dtype=np.float32, order='F')

def cuda_set_device(dev_id):
    """
    Selects the CUDA device with the given ID.
    """

    err_code =  _cudamat.cuda_set_device(ct.c_int(dev_id))
    if err_code:
        raise generate_exception(err_code)

def cublas_init():
    """
    Initialize Cublas.
    """

    _cudamat.cublas_init()
    CUDAMatrix.ones = CUDAMatrix(np.ones((MAX_ONES, 1), dtype=np.float32, order = 'F'))

init = cublas_init

def cublas_shutdown():
    """
    Shut down Cublas.
    """

    CUDAMatrix.ones = 0
    _cudamat.cublas_shutdown()

shutdown = cublas_shutdown
