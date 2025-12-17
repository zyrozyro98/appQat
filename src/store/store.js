// src/store/store.js
import { createStore, applyMiddleware } from 'redux';
import { persistStore, persistReducer } from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import thunk from 'redux-thunk';
import rootReducer from './reducers';

const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['auth', 'cart'],
};

const persistedReducer = persistReducer(persistConfig, rootReducer);
const store = createStore(persistedReducer, applyMiddleware(thunk));
const persistor = persistStore(store);

export { store, persistor };

// src/store/reducers/index.js
import { combineReducers } from 'redux';
import authReducer from './authReducer';
import cartReducer from './cartReducer';
import productsReducer from './productsReducer';
import ordersReducer from './ordersReducer';
import usersReducer from './usersReducer';
import adminReducer from './adminReducer';

export default combineReducers({
  auth: authReducer,
  cart: cartReducer,
  products: productsReducer,
  orders: ordersReducer,
  users: usersReducer,
  admin: adminReducer,
});

// src/store/reducers/authReducer.js
const initialState = {
  user: null,
  token: null,
  loading: false,
  error: null,
  userType: null, // 'buyer', 'seller', 'admin', 'driver', 'washer'
};

export default function authReducer(state = initialState, action) {
  switch (action.type) {
    case 'LOGIN_REQUEST':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        loading: false,
        user: action.payload.user,
        token: action.payload.token,
        userType: action.payload.user.userType,
      };
    case 'LOGIN_FAILURE':
      return { ...state, loading: false, error: action.payload };
    case 'LOGOUT':
      return initialState;
    case 'UPDATE_BALANCE':
      return {
        ...state,
        user: {
          ...state.user,
          balance: action.payload,
        },
      };
    default:
      return state;
  }
}
