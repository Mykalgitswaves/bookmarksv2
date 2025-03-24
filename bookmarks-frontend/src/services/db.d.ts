declare module '@/services/db' {
  export const db: {
    get: (url: string, params?: any, debug: Boolean, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
    post: (url: string, data: any, debug: Boolean, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
    put: (url: string, data?: any, debug: Boolean, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
  };
} 