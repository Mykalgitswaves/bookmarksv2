declare module '@/services/db' {
  export const db: {
    get: (url: string, params?: any, cache?: boolean, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
    post: (url: string, data: any, cache?: boolean, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
    put: (url: string, data?: any, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
    delete: (url: string, onSuccess?: (res: any) => void, onError?: (err: any) => void) => Promise<any>;
  };
} 