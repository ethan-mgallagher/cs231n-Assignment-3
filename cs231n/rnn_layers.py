from __future__ import print_function, division
from builtins import range
import numpy as np


"""
This file defines layer types that are commonly used for recurrent neural
networks.
"""


def rnn_step_forward(x, prev_h, Wx, Wh, b):
    """
    Run the forward pass for a single timestep of a vanilla RNN that uses a tanh
    activation function.

    The input data has dimension D, the hidden state has dimension H, and we use
    a minibatch size of N.

    Inputs:
    - x: Input data for this timestep, of shape (N, D).
    - prev_h: Hidden state from previous timestep, of shape (N, H)
    - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
    - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
    - b: Biases of shape (H,)

    Returns a tuple of:
    - next_h: Next hidden state, of shape (N, H)
    - cache: Tuple of values needed for the backward pass.
    """
    next_h, cache = None, None
    ##############################################################################
    # TODO: Implement a single forward step for the vanilla RNN. Store the next  #
    # hidden state and any values you need for the backward pass in the next_h   #
    # and cache variables respectively.                                          #
    ##############################################################################

    h_term = np.dot( prev_h, Wh )
    x_term = np.dot( x, Wx )
    tanh_term = h_term + x_term + b
    next_h = np.tanh( tanh_term )

    cache = next_h, prev_h, x, Wx, Wh
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return next_h, cache


def rnn_step_backward(dnext_h, cache):
    """
    Backward pass for a single timestep of a vanilla RNN.

    Inputs:
    - dnext_h: Gradient of loss with respect to next hidden state
    - cache: Cache object from the forward pass

    Returns a tuple of:
    - dx: Gradients of input data, of shape (N, D)
    - dprev_h: Gradients of previous hidden state, of shape (N, H)
    - dWx: Gradients of input-to-hidden weights, of shape (D, H)
    - dWh: Gradients of hidden-to-hidden weights, of shape (H, H)
    - db: Gradients of bias vector, of shape (H,)
    """
    dx, dprev_h, dWx, dWh, db = None, None, None, None, None
    ##############################################################################
    # TODO: Implement the backward pass for a single step of a vanilla RNN.      #
    #                                                                            #
    # HINT: For the tanh function, you can compute the local derivative in terms #
    # of the output value from tanh.                                             #
    ##############################################################################
    next_h, prev_h, x, Wx, Wh = cache
    N, D, H = x.shape[0], x.shape[1], Wx.shape[1]

    dtanh = ( 1 - ( next_h * next_h )) * dnext_h
    dxterm = dtanh
    dhterm = dtanh
    db = np.sum( dtanh, axis=0)
    dWx = np.dot( x.T, dxterm )
    dWh = np.dot( prev_h.T, dhterm )
    dx = np.dot( dxterm, Wx.T )
    dprev_h = np.dot( dhterm, Wh.T)

    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return dx, dprev_h, dWx, dWh, db


def rnn_forward(x, h0, Wx, Wh, b):
    """
    Run a vanilla RNN forward on an entire sequence of data. We assume an input
    sequence composed of T vectors, each of dimension D. The RNN uses a hidden
    size of H, and we work over a minibatch containing N sequences. After running
    the RNN forward, we return the hidden states for all timesteps.

    Inputs:
    - x: Input data for the entire timeseries, of shape (N, T, D).
    - h0: Initial hidden state, of shape (N, H)
    - Wx: Weight matrix for input-to-hidden connections, of shape (D, H)
    - Wh: Weight matrix for hidden-to-hidden connections, of shape (H, H)
    - b: Biases of shape (H,)

    Returns a tuple of:
    - h: Hidden states for the entire timeseries, of shape (N, T, H).
    - cache: Values needed in the backward pass
    """
    h, cache = None, None
    ##############################################################################
    # TODO: Implement forward pass for a vanilla RNN running on a sequence of    #
    # input data. You should use the rnn_step_forward function that you defined  #
    # above. You can use a for loop to help compute the forward pass.            #
    ##############################################################################
    N, T, D, H = x.shape[0], x.shape[1], x.shape[2], b.shape[0]
    x = x.transpose( 1, 0, 2 )
    h = np.zeros( shape=(T, N, H))
    cache = {}

    for t in range(0, T):
        if t == 0:
            cur_h = h0
        cur_h, cur_cache = rnn_step_forward( x[t,:,:], cur_h, Wx, Wh, b)
        cache[ t ] = cur_cache
        h[t] = cur_h

    h = h.transpose( 1, 0, 2 )
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return h, cache


def rnn_backward(dh, cache):
    """
    Compute the backward pass for a vanilla RNN over an entire sequence of data.

    Inputs:
    - dh: Upstream gradients of all hidden states, of shape (N, T, H)

    Returns a tuple of:
    - dx: Gradient of inputs, of shape (N, T, D)
    - dh0: Gradient of initial hidden state, of shape (N, H)
    - dWx: Gradient of input-to-hidden weights, of shape (D, H)
    - dWh: Gradient of hidden-to-hidden weights, of shape (H, H)
    - db: Gradient of biases, of shape (H,)
    """
    dx, dh0, dWx, dWh, db = None, None, None, None, None
    ##############################################################################
    # TODO: Implement the backward pass for a vanilla RNN running an entire      #
    # sequence of data. You should use the rnn_step_backward function that you   #
    # defined above. You can use a for loop to help compute the backward pass.   #
    ##############################################################################
    dim_x = cache[0][2]
    N, T, H, D = dh.shape[0], dh.shape[1], dh.shape[2], dim_x.shape[1]

    dx = np.zeros( shape=( T, N, D ) )
    dWx = np.zeros( shape=(D, H))
    dWh = np.zeros( shape=(H, H) )
    db = np.zeros( shape=( H, ))
    dh = dh.transpose( 1, 0, 2 )

    for t in range(T-1, -1, -1 ):
        if t == ( T - 1 ):
            dprev_h = np.zeros( shape=(dh[t].shape ))
        cur_cache = cache[t]
        cur_dx, dprev_h, cur_dWx, cur_dWh, cur_db = rnn_step_backward( dh[t] + dprev_h, cur_cache )
        dx[t] = cur_dx
        dWx += cur_dWx
        dWh += cur_dWh
        db += cur_db
        if t == 0:
            dh0 = dprev_h

    dx = dx.transpose( 1, 0, 2 )


    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return dx, dh0, dWx, dWh, db


def word_embedding_forward(x, W):
    """
    Forward pass for word embeddings. We operate on minibatches of size N where
    each sequence has length T. We assume a vocabulary of V words, assigning each
    to a vector of dimension D.

    Inputs:
    - x: Integer array of shape (N, T) giving indices of words. Each element idx
      of x muxt be in the range 0 <= idx < V.
    - W: Weight matrix of shape (V, D) giving word vectors for all words.

    Returns a tuple of:
    - out: Array of shape (N, T, D) giving word vectors for all input words.
    - cache: Values needed for the backward pass
    """
    out, cache = None, None
    ##############################################################################
    # TODO: Implement the forward pass for word embeddings.                      #
    #                                                                            #
    # HINT: This can be done in one line using NumPy's array indexing.           #
    ##############################################################################
    out = W[ x, :]
    cache = x, W
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return out, cache


def word_embedding_backward(dout, cache):
    """
    Backward pass for word embeddings. We cannot back-propagate into the words
    since they are integers, so we only return gradient for the word embedding
    matrix.

    HINT: Look up the function np.add.at

    Inputs:
    - dout: Upstream gradients of shape (N, T, D)
    - cache: Values from the forward pass

    Returns:
    - dW: Gradient of word embedding matrix, of shape (V, D).
    """
    dW = None
    ##############################################################################
    # TODO: Implement the backward pass for word embeddings.                     #
    #                                                                            #
    # Note that Words can appear more than once in a sequence.                   #
    # HINT: Look up the function np.add.at                                       #
    ##############################################################################
    x, W = cache
    N, T, D = dout.shape
    dW = np.zeros( shape=( W.shape ))

    flat_x = x.reshape( N * T )
    flat_dout = dout.reshape( N*T, D)

    np.add.at( dW, flat_x, flat_dout[ np.arange( N *T ) ])

    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################
    return dW


def sigmoid(x):
    """
    A numerically stable version of the logistic sigmoid function.
    """
    pos_mask = (x >= 0)
    neg_mask = (x < 0)
    z = np.zeros_like(x)
    z[pos_mask] = np.exp(-x[pos_mask])
    z[neg_mask] = np.exp(x[neg_mask])
    top = np.ones_like(x)
    top[neg_mask] = z[neg_mask]
    return top / (1 + z)


def lstm_step_forward(x, prev_h, prev_c, Wx, Wh, b):
    """
    Forward pass for a single timestep of an LSTM.

    The input data has dimension D, the hidden state has dimension H, and we use
    a minibatch size of N.

    Inputs:
    - x: Input data, of shape (N, D)
    - prev_h: Previous hidden state, of shape (N, H)
    - prev_c: previous cell state, of shape (N, H)
    - Wx: Input-to-hidden weights, of shape (D, 4H)
    - Wh: Hidden-to-hidden weights, of shape (H, 4H)
    - b: Biases, of shape (4H,)

    Returns a tuple of:
    - next_h: Next hidden state, of shape (N, H)
    - next_c: Next cell state, of shape (N, H)
    - cache: Tuple of values needed for backward pass.
    """
    next_h, next_c, cache = None, None, None
    #############################################################################
    # TODO: Implement the forward pass for a single timestep of an LSTM.        #
    # You may want to use the numerically stable sigmoid implementation above.  #
    #############################################################################

    ##get dimensions
    N, D, H = prev_h.shape[0], Wx.shape[0], prev_h.shape[1]

    #compute activation matrix, dimensions are (N, 4H)
    act_vec = np.dot( x, Wx ) + np.dot( prev_h, Wh ) + b

    ##slice into activation matrix to get activation vectors
    ai, af, ao, ag = act_vec[:,0:H], act_vec[:,H:2*H], act_vec[:,2*H:3*H], act_vec[:,3*H:4*H]

    ##compute gates

    i = sigmoid( ai )
    f = sigmoid( af )
    o = sigmoid( ao )
    g = np.tanh( ag )

    next_c = f * prev_c + i * g
    squashed = np.tanh( next_c )
    next_h = o * squashed

    cache = i, f, o, g, prev_c, prev_h, x, squashed, Wh, Wx

    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################

    return next_h, next_c, cache


def lstm_step_backward(dnext_h, dnext_c, cache):
    """
    Backward pass for a single timestep of an LSTM.

    Inputs:
    - dnext_h: Gradients of next hidden state, of shape (N, H)
    - dnext_c: Gradients of next cell state, of shape (N, H)
    - cache: Values from the forward pass

    Returns a tuple of:
    - dx: Gradient of input data, of shape (N, D)
    - dprev_h: Gradient of previous hidden state, of shape (N, H)
    - dprev_c: Gradient of previous cell state, of shape (N, H)
    - dWx: Gradient of input-to-hidden weights, of shape (D, 4H)
    - dWh: Gradient of hidden-to-hidden weights, of shape (H, 4H)
    - db: Gradient of biases, of shape (4H,)
    """
    dx, dh, dc, dWx, dWh, db = None, None, None, None, None, None
    #############################################################################
    # TODO: Implement the backward pass for a single timestep of an LSTM.       #
    #                                                                           #
    # HINT: For sigmoid and tanh you can compute local derivatives in terms of  #
    # the output value from the nonlinearity.                                   #
    #############################################################################
    i, f, o, g, prev_c, prev_h, x, squashed, Wh, Wx = cache
    N, H, D = dnext_h.shape[0], dnext_h.shape[1], x.shape[1]

    dsquashed = o * dnext_h
    dadd_c = (1 - (squashed * squashed))* dsquashed
    dnext_c += dadd_c

    dg_next = i * dnext_c
    df_next = dnext_c * prev_c
    di_next = g * dnext_c
    do_next = squashed * dnext_h
    dprev_c = f * dnext_c

    ##backprop through non-linearities
    dg = ( 1 - (g*g)) * dg_next
    df = f*(1-f) * df_next
    di = i * (1 - i) * di_next
    do = o * (1 - o) * do_next

    ##put them back into the activation matrix
    dact_vec = np.zeros( shape=( N, 4*H) )

    dact_vec[:,0:H] = di
    dact_vec[:,H:2*H] = df
    dact_vec[:,2*H:3*H] = do
    dact_vec[:,3*H:4*H] = dg

    db = np.sum( dact_vec, axis=0)
    dWx = np.dot( x.T, dact_vec)
    dWh = np.dot( prev_h.T, dact_vec )
    dprev_h = np.dot( dact_vec, Wh.T )
    dx = np.dot( dact_vec, Wx.T )

    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################

    return dx, dprev_h, dprev_c, dWx, dWh, db


def lstm_forward(x, h0, Wx, Wh, b):
    """
    Forward pass for an LSTM over an entire sequence of data. We assume an input
    sequence composed of T vectors, each of dimension D. The LSTM uses a hidden
    size of H, and we work over a minibatch containing N sequences. After running
    the LSTM forward, we return the hidden states for all timesteps.

    Note that the initial cell state is passed as input, but the initial cell
    state is set to zero. Also note that the cell state is not returned; it is
    an internal variable to the LSTM and is not accessed from outside.

    Inputs:
    - x: Input data of shape (N, T, D)
    - h0: Initial hidden state of shape (N, H)
    - Wx: Weights for input-to-hidden connections, of shape (D, 4H)
    - Wh: Weights for hidden-to-hidden connections, of shape (H, 4H)
    - b: Biases of shape (4H,)

    Returns a tuple of:
    - h: Hidden states for all timesteps of all sequences, of shape (N, T, H)
    - cache: Values needed for the backward pass.
    """
    h, cache = None, None
    #############################################################################
    # TODO: Implement the forward pass for an LSTM over an entire timeseries.   #
    # You should use the lstm_step_forward function that you just defined.      #
    #############################################################################
    N, T, D, H = x.shape[0], x.shape[1], x.shape[2], h0.shape[1]

    #into dims (T, N, D)
    x = x.transpose( 1, 0, 2 )
    h = np.zeros( shape=(T, N, H ))
    cache = {}

    for t in range( 0, T ):
        if t == 0:
            cur_h = h0
            cur_c = np.zeros( shape=(cur_h.shape))
        cur_h, cur_c, cache[t] = lstm_step_forward(x[t], cur_h, cur_c, Wx, Wh, b)
        h[t] = cur_h

    h = h.transpose( 1, 0, 2 )
    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################

    return h, cache


def lstm_backward(dh, cache):
    """
    Backward pass for an LSTM over an entire sequence of data.]

    Inputs:
    - dh: Upstream gradients of hidden states, of shape (N, T, H)
    - cache: Values from the forward pass

    Returns a tuple of:
    - dx: Gradient of input data of shape (N, T, D)
    - dh0: Gradient of initial hidden state of shape (N, H)
    - dWx: Gradient of input-to-hidden weight matrix of shape (D, 4H)
    - dWh: Gradient of hidden-to-hidden weight matrix of shape (H, 4H)
    - db: Gradient of biases, of shape (4H,)
    """
    dx, dh0, dWx, dWh, db = None, None, None, None, None
    #############################################################################
    # TODO: Implement the backward pass for an LSTM over an entire timeseries.  #
    # You should use the lstm_step_backward function that you just defined.     #
    #############################################################################

    dim_x = cache[0][6]
    N, T, H, D = dh.shape[0], dh.shape[1], dh.shape[2], dim_x.shape[1]

    dx = np.zeros( shape=(T, N, D))
    dh0 = np.zeros( shape=(N, H))
    dWx = np.zeros( shape=(D, 4*H))
    dWh = np.zeros( shape=(H, 4*H))
    db = np.zeros( shape=(4*H,))
    dh = dh.transpose( 1, 0, 2)

    for t in range(T - 1, -1, -1):
        if t == (T - 1):
            dprev_h = np.zeros(shape=(dh[t].shape))
            dprev_c = np.zeros( shape=(dh[t].shape))
        cur_cache = cache[t]
        cur_dx, dprev_h, dprev_c, cur_dWx, cur_dWh, cur_db = lstm_step_backward(dh[t] + dprev_h, dprev_c, cur_cache)
        dx[t] = cur_dx
        dWx += cur_dWx
        dWh += cur_dWh
        db += cur_db
        if t == 0:
            dh0 = dprev_h

    dx = dx.transpose(1, 0, 2)


    ##############################################################################
    #                               END OF YOUR CODE                             #
    ##############################################################################

    return dx, dh0, dWx, dWh, db


def temporal_affine_forward(x, w, b):
    """
    Forward pass for a temporal affine layer. The input is a set of D-dimensional
    vectors arranged into a minibatch of N timeseries, each of length T. We use
    an affine function to transform each of those vectors into a new vector of
    dimension M.

    Inputs:
    - x: Input data of shape (N, T, D)
    - w: Weights of shape (D, M)
    - b: Biases of shape (M,)

    Returns a tuple of:
    - out: Output data of shape (N, T, M)
    - cache: Values needed for the backward pass
    """
    N, T, D = x.shape
    M = b.shape[0]
    out = x.reshape(N * T, D).dot(w).reshape(N, T, M) + b
    cache = x, w, b, out
    return out, cache


def temporal_affine_backward(dout, cache):
    """
    Backward pass for temporal affine layer.

    Input:
    - dout: Upstream gradients of shape (N, T, M)
    - cache: Values from forward pass

    Returns a tuple of:
    - dx: Gradient of input, of shape (N, T, D)
    - dw: Gradient of weights, of shape (D, M)
    - db: Gradient of biases, of shape (M,)
    """
    x, w, b, out = cache
    N, T, D = x.shape
    M = b.shape[0]

    dx = dout.reshape(N * T, M).dot(w.T).reshape(N, T, D)
    dw = dout.reshape(N * T, M).T.dot(x.reshape(N * T, D)).T
    db = dout.sum(axis=(0, 1))

    return dx, dw, db


def temporal_softmax_loss(x, y, mask, verbose=False):
    """
    A temporal version of softmax loss for use in RNNs. We assume that we are
    making predictions over a vocabulary of size V for each timestep of a
    timeseries of length T, over a minibatch of size N. The input x gives scores
    for all vocabulary elements at all timesteps, and y gives the indices of the
    ground-truth element at each timestep. We use a cross-entropy loss at each
    timestep, summing the loss over all timesteps and averaging across the
    minibatch.

    As an additional complication, we may want to ignore the model output at some
    timesteps, since sequences of different length may have been combined into a
    minibatch and padded with NULL tokens. The optional mask argument tells us
    which elements should contribute to the loss.

    Inputs:
    - x: Input scores, of shape (N, T, V)
    - y: Ground-truth indices, of shape (N, T) where each element is in the range
         0 <= y[i, t] < V
    - mask: Boolean array of shape (N, T) where mask[i, t] tells whether or not
      the scores at x[i, t] should contribute to the loss.

    Returns a tuple of:
    - loss: Scalar giving loss
    - dx: Gradient of loss with respect to scores x.
    """

    N, T, V = x.shape

    x_flat = x.reshape(N * T, V)
    y_flat = y.reshape(N * T)
    mask_flat = mask.reshape(N * T)

    probs = np.exp(x_flat - np.max(x_flat, axis=1, keepdims=True))
    probs /= np.sum(probs, axis=1, keepdims=True)
    loss = -np.sum(mask_flat * np.log(probs[np.arange(N * T), y_flat])) / N
    dx_flat = probs.copy()
    dx_flat[np.arange(N * T), y_flat] -= 1
    dx_flat /= N
    dx_flat *= mask_flat[:, None]

    if verbose: print('dx_flat: ', dx_flat.shape)

    dx = dx_flat.reshape(N, T, V)

    return loss, dx

if __name__ == "__main__":
    from cs231n.gradient_check import eval_numerical_gradient, eval_numerical_gradient_array

    def rel_error(x, y):
        """ returns relative error """
        return np.max(np.abs(x - y) / (np.maximum(1e-8, np.abs(x) + np.abs(y))))

