// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.

/**
 * Authentication hook for Songo BI
 */

import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../store';
import { authActions, getCurrentUser } from '../store/slices/authSlice';

export const useAuth = () => {
  const dispatch = useDispatch();
  const { isAuthenticated, user, isLoading, error, token } = useSelector(
    (state: RootState) => state.auth
  );

  useEffect(() => {
    // Check for existing token and validate user
    if (token && !user && !isLoading) {
      dispatch(getCurrentUser());
    }
  }, [token, user, isLoading, dispatch]);

  const login = (credentials: { username: string; password: string }) => {
    return dispatch(authActions.login(credentials));
  };

  const logout = () => {
    return dispatch(authActions.logout());
  };

  const clearError = () => {
    dispatch(authActions.clearError());
  };

  return {
    isAuthenticated,
    user,
    isLoading,
    error,
    login,
    logout,
    clearError,
  };
};
