export type ApiResult<T> =
  | { data: T; error: null }
  | { data: null; error: ApiError };

export interface ApiError {
  error_code: string;
  message: string;
  status?: number;
}
