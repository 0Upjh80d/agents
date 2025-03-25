import { Component, Input, ElementRef, Renderer2, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-markdown',
  standalone: true,
  imports: [CommonModule, MarkdownModule],
  templateUrl: './markdown.component.html',
  styleUrls: ['./markdown.component.css']
})
export class MarkdownComponent implements OnChanges {
  @Input() markdownContent?: string = `# Default Markdown Content`;

  constructor(private el: ElementRef, private renderer: Renderer2) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['markdownContent']) {
      setTimeout(() => {
        this.updateLinksTarget();
      }, 0);
    }
  }

  private updateLinksTarget() {
    const element = this.el.nativeElement as HTMLElement;
    const links = element.querySelectorAll('a'); // Finds anchor tags in the markdown content

    links.forEach(link => {
      this.renderer.setAttribute(link, 'target', '_blank');
      this.renderer.setAttribute(link, 'rel', 'noopener noreferrer');
    });
  }
}
