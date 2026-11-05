// Small browser entry point; each scale and shared feature is a native module.
import { boot } from './src/app/bootstrap.js';

await boot();
