import { TestBed } from '@angular/core/testing';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
    })
      .compileComponents();
  });

  it('mostra o nome do produto', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(fixture.nativeElement.querySelector('h1')?.textContent).toContain('Nihongo Lab');
  });
});
